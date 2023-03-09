## Hoshuko Absence Tracker

This application will allow parents to register their students absences

### DB Setup

Initialize the database with:
`flask db init`

create the SQLite file with:
`flask db migrate -m "initial db"`

If you upgrade the model, update the db with:
`flask db upgrade`

