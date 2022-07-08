#!/usr/bin/env python3

import click
import chevron
from datetime import datetime, timezone
import psycopg2 as pg


def run_command(db, command_string):
    conn = pg.connect(db)
    cur = conn.cursor()
    cur.execute(command_string)

    cur.commit()



@click.command()
@click.option("--index", prompt="Enter the database index")
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
    print(index, descr, full_descr, display_name)
    argument_dict = {"index" : index,
                   "descr": descr,
                   "full_descr": full_descr,
                   "display_name": display_name,
                   "timestamp": datetime.now(tz=None).isoformat()}

    ## render the insert command using chevron
    with open("templates/database-entry.mustache", 'r') as entry_template:
        entry = chevron.render(entry_template, argument_dict)

    with open("templates/partition.mustache", 'r') as part_template:
        partition = chevron.render(part_template, argument_dict)

    with open("templates/xref-function.mustache", 'r') as xref_template:
        xref = chevron.render(xref_template, argument_dict)


    if dry_run or print_rendered:
        print("Rendered INSERT command as:")
        print(entry)
        print("----------------------------------")
        print("Rendered partition command as:")
        print(partition)
        print("----------------------------------")
        print("Rendered xref function as:")
        print(xref)
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
            run_command(db, entry)
            run_command(db, partition)
            run_command(db, xref)
            print("Done!")





if __name__ == "__main__":
    main()
