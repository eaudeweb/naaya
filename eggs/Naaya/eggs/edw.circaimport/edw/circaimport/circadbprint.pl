#!/opt/circa21/bin/perl
# db2gdbm: converts DB to GDBM

#use strict;

use DB_File;

if (@ARGV < 1) {
    die "usage: dbprint infile\n";
}

my ($infile) = @ARGV;
my (%db_in);

# open the file
tie(%db_in, 'DB_File', $infile) or die "Can't tie $infile: $!";

while (my($k, $v) = each %db_in) {
    printf "%s\t%s\n",$k, $v;
}

untie %db_in;
