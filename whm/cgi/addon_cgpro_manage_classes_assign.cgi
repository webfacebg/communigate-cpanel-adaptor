#!/usr/bin/perl

use lib '/usr/local/cpanel';
use Cpanel::Form            ();
use Whostmgr::HTMLInterface ();
use Whostmgr::ACLS          ();
use CLI;
use Cpanel::API::Branding        ();
use Cpanel::CachedDataStore;

print "Content-type: text/html\r\n\r\n";

Whostmgr::ACLS::init_acls();
if ( !Whostmgr::ACLS::hasroot() ) {
  print "You need to be root to see this page.\n";
  exit();
}

my $conf = Cpanel::CachedDataStore::fetch_ref( '/var/cpanel/communigate.yaml' ) || {};
my $cli = new CGP::CLI( { PeerAddr => $conf->{cgprohost},
                            PeerPort => $conf->{cgproport},
                            login => $conf->{cgprouser},
                            password => $conf->{cgpropass} } );
unless($cli) {
  print STDERR "Can't login to CGPro: ".$CGP::ERR_STRING,"\n";
   exit(0);
}

my $cgproversion = $cli->getversion();

my %FORM = Cpanel::Form::parseform();

Whostmgr::HTMLInterface::defheader( "CGPro Manage Classes for " . $FORM{domain},'', '/cgi/addon_cgp_manage_classes_assign.cgi' );

# Mail delimiter
my $defaults = $cli->GetServerAccountDefaults();
# check if domain is defined in CGPro;
my $domain = $cli->GetDomainSettings($FORM{domain});
my $data = Cpanel::CachedDataStore::fetch_ref( '/var/cpanel/cgpro/classes.yaml' ) || {};
if ($FORM{'save'}) {
    $data->{$FORM{'domain'}} = {};
    for my $class (keys %{$defaults->{ServiceClasses}}) {
	$data->{$FORM{'domain'}}->{$class}->{'all'} = $FORM{$class . '-all'};
	$data->{$FORM{'domain'}}->{$class}->{'free'} = $FORM{$class . '-free'};
    }
    Cpanel::CachedDataStore::store_ref( '/var/cpanel/cgpro/classes.yaml', $data );
}


Cpanel::Template::process_template(
				   'whostmgr',
				   {
				    'template_file' => 'addon_cgpro_manage_classes_assign.tmpl',
				    defaults => $defaults,
				    domain_data => $data->{$FORM{'domain'}},
				    domain => $FORM{domain},
				    domain_defined => $domain,
				    cgproversion => $cgproversion
				   },
				  );

$cli->Logout();
1;