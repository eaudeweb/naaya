#!/opt/circa21/bin/perl
# db2gdbm: converts DB to GDBM

#use strict;

use DB_File;
use GDBM_File;

if (@ARGV < 1) {
    die "usage: gdbm2db infile [outfile]\n";
}

my ($infile, $outfile) = @ARGV;
unless ($outfile) {
        $outfile = $infile;
        unless ($outfile =~ s/\.db$/.gdbm/) {
                $outfile = $outfile . '.gdbm';
        }
}
my (%db_in, %db_out);

# open the files
tie(%db_in, 'DB_File', $infile) or die "Can't tie $infile: $!";
tie(%db_out, 'GDBM_File', $outfile, GDBM_WRCREAT, 0) or die "Can't tie $outfile: $!";

# copy (don't use %db_out = %db_in because it's slow on big databases)
while (my($k, $v) = each %db_in) {
    $db_out{$k} = $v;
}

# these unties happen automatically at program exit
untie %db_in;
untie %db_out;
