#!/usr/bin/env python3

import click
import chevron
from datetime import datetime, timezone
import psycopg2 as pg
import re


class DBContext:
    def __init__(self, db_url):
        self.connection = pg.connect(db_url)

    def run_command(self, command_string):
        cur = self.connection.cursor()
        try:
            cur.execute(command_string)
        except pg.ProgrammingError as e:
            print("Syntax probably wrong:")
            print(e.pgerror)
            print(command_string)
            print("Aborting...")
            exit()
        except pg.Error as e:
            print("Some other error")
            print(e.pgerror)
            print(command_string)
            exit()
        except pg.Warning as w:
            print(w.pgerror)

        return cur

    def commit_changes(self):
        self.connection.commit()

    def rollback_changes(self):
        self.connection.rollback()



def get_next_index(context):
    cur = context.run_command("select max(id) from rnc_database")
    return cur.fetchone()[0] + 1

def get_xref_trigger_fcn(context):
    cur = context.run_command("select pg_get_functiondef('rnacen.xref_insert_trigger()'::regprocedure)")
    return cur.fetchone()[0]


def splice_xref_function(original, insertion, index):

    # first find the elif matching the last index
    regex_elsif = re.compile("^\s*(?:ELS)*IF \( NEW\.DB", re.MULTILINE)
    last_elif_start = None
    for idx, p in enumerate(regex_elsif.finditer(original), 1):
        if idx == index - 1:
            last_elif_start = p.start()

    ## find the end of the last index elif block
    regex_endif = re.compile("END IF;\n")

    end_match = regex_endif.search(original, last_elif_start)
    insert_start = end_match.end()

    # insert our modification in the right place
    modified_fcn = "".join((original[:insert_start], insertion, original[insert_start:]))

    return modified_fcn

@click.command()
@click.option("--index", default=None, type=int, help="Enter the database index")
@click.option("--descr", prompt="Enter the database short description")
@click.option("--full_descr", prompt="Enter the database full description")
@click.option("--display_name", prompt="Enter the database display name")
@click.option("--db", envvar="PGDATABASE",help="The database connection string. Taken from environment if possible")
@click.option("--dry_run", is_flag=True, help="Render templates and print them, but dont change the database" )
@click.option("--print_rendered", is_flag=True, help="Print rendered templates")
def main(index, descr, full_descr, display_name, db, dry_run, print_rendered):
    """
    Quick utility to produce and run necessary SQL commands
    for adding a new database in RNAcentral
    """

    context = DBContext(db)

    if index is None:
        index = get_next_index(context)

    trigger_fcn = get_xref_trigger_fcn(context)

    if len(descr) >= 60:
        print("Description string too long! (< 60)")
        return 1

    if len(full_descr) >= 1024:
        print("Full descrtption too long! (< 1024)")
        return 2

    if len(display_name) >= 60:
        print("Display name too long! (< 60)")
        return 3


    argument_dict = {"index" : index,
                   "descr": descr,
                   "full_descr": full_descr,
                   "display_name": display_name,
                   "timestamp": datetime.now(tz=None).isoformat()}

    print(argument_dict)
    ## render the insert command using chevron
    with open("templates/database-entry.mustache", 'r') as entry_template:
        entry = chevron.render(entry_template, argument_dict)

    with open("templates/partition.mustache", 'r') as part_template:
        partition = chevron.render(part_template, argument_dict)

    with open("templates/xref-function.mustache", 'r') as xref_template:
        xref = chevron.render(xref_template, argument_dict)

    xref_new = splice_xref_function(trigger_fcn, xref, index)

    if dry_run or print_rendered:
        print("Rendered INSERT command as:")
        print(entry)
        print("----------------------------------")
        print("Rendered partition command as:")
        print(partition)
        print("----------------------------------")
        print("Rendered xref function as:")
        print(xref_new)
        print("----------------------------------")

    if not dry_run:
        while True:
            confirmation = input("About to run the commands in the configured database, do you want to continue?")
            if confirmation not in ["yes", "no"]:
                print("Please type yes or no")
            else:
                break
        if confirmation == "no":
            print("Aborting...")
        else:
            print("Running commands...")
            context.run_command(entry)
            context.run_command(partition)
            context.run_command(xref_new)
            print("Done!")





if __name__ == "__main__":
    main()
