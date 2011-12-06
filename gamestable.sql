create table if not exists games (
    id          integer primary key,
    wplayerid   integer,
    bplayerid   integer,
    wrating     integer,
    brating     integer,
    wtype       varchar(1),
    btype       varchar(1),
    result      varchar(1),
    termination varchar(1),
    movelist    text);

