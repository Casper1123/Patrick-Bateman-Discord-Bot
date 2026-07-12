# Data
The Data folder contains a bunch of files that I might want to explain how and what everything works.

## Interfaces
The `interfaces` folders contain individually prepared Abstract Base Classes (ABC) that need to be implemented by some implementation to be usable in the application.
It specifies only the callable functions and specifically required parameters and functionality, but (which an interface does) leaves all implementation to the actual inheritor.
I'm using this not because I like design patterns (yuck) but because this is my first time trying to screw around with SQL for a hobby project, and I wanted something I could potentially swap out without having to rewrite too much shit.

## Data
The subfolder `data` exists to hold actual database files. As such, that is where data is stored.

## Schemas
SQL schemas used to create a db file if it does not exist yet. Implementation use only.

## admin_help
Markdown file whose content is given in the help command for admins. `<BR>` replaced with newlines.
todo: actually make this work pretty please

## Implementation
SQL implementation attempts for different components of the application