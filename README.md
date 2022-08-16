# rnacentral-new-db-import
Code to create the needed tables and other changes in the RNAcentral database for new imports


Based on the code originally developed by Blake Sweeney (https://github.com/blakesweeney/new-db-flow)

## Help output
Usage: add-db.py [OPTIONS]

  Quick utility to produce and run necessary SQL commands for adding a new
  database in RNAcentral

Options:
  --index INTEGER      Enter the database index
  --descr TEXT
  --full_descr TEXT
  --display_name TEXT
  --db TEXT            The database connection string. Taken from environment
                       if possible

  --dry_run            Render templates and print them, but dont change the
                       database

  --print_rendered     Print rendered templates
  --help               Show this message and exit.

## Example usage

_NB: I have a file which I use to make the DB URL into an environment variable, so it doesn't get specified in the command_

The tool can run in interactive mode, and will prompt you for the necessary information. When importing PLncDB I ran 
```
python add-db.py --dry_run
```
And at the interactive prompt gave the following answers, and got the dictionary with the necessary information:

```
Enter the database short description: PLNCDB
Enter the database full description: PLncDB
Enter the database display name: PLncDB
{'index': 50, 'descr': 'PLNCDB', 'full_descr': 'PLncDB', 'display_name': 'PLncDB', 'timestamp': '2022-08-16T15:41:01.347640'}
```
Some bits of the info are autofilled, like the index which will just jump to the next available if you don't specify otherwise.

After that the rendered SQL is printed, since I did a dry run, and the program exits

**Always do a dry run and inspect the SQL**

After that, you can run again without `--dry_run` to make the changes in the database. I would reccomend still running with `--print_rendered` so you can inspect the SQL. The code will ask for confirmation before committing your changes to the database, and that should be it!
