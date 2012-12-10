%define ecllibdir		%{_libdir}/%{name}-%{version}

%define before_configure	true
%define _disable_libtoolize	%{nil}

Name:           ecl
Version:        12.7.1
Release:        1
Summary:        Embeddable Common-Lisp
Group:          Development/Other
License:        LGPLv2+
URL:            http://ecls.sourceforge.net
Source0:        http://switch.dl.sourceforge.net/sourceforge/ecls/%{name}-%{version}.tar.gz

BuildRequires:  m4
BuildRequires:  texi2html
BuildRequires:	texinfo
#BuildRequires:	texlive
BuildRequires:  gmp-devel
BuildRequires:  pkgconfig(bdw-gc)
BuildRequires:  pkgconfig(x11)

# ECL permits to mix C code and Lisp, so users probably want gcc and 
# devel packages of libraries used by ecl
Suggests:       gcc
Suggests:       pkgconfig(bdw-gc)
Suggests:       gmp-devel

%description
ECL (Embeddable Common-Lisp) is an interpreter of the Common-Lisp
language as described in the X3J13 Ansi specification, featuring CLOS
(Common-Lisp Object System), conditions, loops, etc, plus a translator
to C, which can produce standalone executables.

# no -devel package for header files is split off
# since they are required by the main package

%package doc
Summary:      Documentation for Embeddable Common-Lisp
Group:        Development/Other
Requires:     %{name} = %{version}

%description doc
ECL (Embeddable Common-Lisp) is an interpreter of the Common-Lisp
language as described in the X3J13 Ansi specification, featuring CLOS
(Common-Lisp Object System), conditions, loops, etc, plus a translator
to C, which can produce standalone executables.

This package contains the documentation for ECL.

%prep
%setup -q
# set rpath to the final path
perl -pi -e 's|-Wl,--rpath,~A|-Wl,--rpath,%{_libdir}/ecl|' src/configure
find -name CVS | xargs rm -rf

%build
CONFIGURE_TOP=. \
%configure --enable-boehm=system --enable-threads=yes --with-clx --with-x
# Parallel make does not work
make

# documentation build broken
#(cd build/doc; make)

%install
%makeinstall_std

# documentation build broken
#(cd build/doc; %makeinstall_std)

# install man pages without invoking broken make rules and remove wrongly
# installed files
mkdir -p %{buildroot}/%{_mandir}/man1
cp -f build/doc/ecl{,-config}.man %{buildroot}/%{_mandir}/man1
lzma %{buildroot}/%{_mandir}/man1/*
rm -f %{buildroot}%{_libdir}/{Copyright,LGPL}

rm -fr %{buildroot}%{_infodir}/dir
rm -fr %{buildroot}%{_docdir}
rm -f %{buildroot}/%{ecllibdir}/BUILD-STAMP
find %{buildroot}%{ecllibdir} -name '*.lsp' | xargs chmod 0644 ||:

%files
%{_bindir}/ecl
%{_bindir}/ecl-config
%{ecllibdir}
%{_libdir}/libecl.so*
%{_includedir}/ecl
%{_mandir}/man*/*
%doc ANNOUNCEMENT Copyright

%files doc
%doc examples


%changelog
* Mon Apr 11 2011 Paulo Andrade <pcpa@mandriva.com.br> 11.1.1-2mdv2011.0
+ Revision: 652725
- Rebuild with gcc 4.6.0

* Thu Jan 27 2011 Paulo Andrade <pcpa@mandriva.com.br> 11.1.1-1
+ Revision: 633432
- Update to ecl 11.1.1.

* Sat Aug 07 2010 Paulo Andrade <pcpa@mandriva.com.br> 10.4.1-1mdv2011.0
+ Revision: 567221
- Update to version 10.0.4.1

* Wed Feb 10 2010 Funda Wang <fwang@mandriva.org> 9.12.3-2mdv2010.1
+ Revision: 503632
- rebuild for new gmp

* Tue Dec 15 2009 Frederik Himpe <fhimpe@mandriva.org> 9.12.3-1mdv2010.1
+ Revision: 479068
- update to new version 9.12.3

* Sat Nov 07 2009 Frederik Himpe <fhimpe@mandriva.org> 9.10.2-1mdv2010.1
+ Revision: 462184
- update to new version 9.10.2

* Tue Aug 18 2009 Frederik Himpe <fhimpe@mandriva.org> 9.8.4-1mdv2010.0
+ Revision: 417840
- update to new version 9.8.4

* Sat Aug 08 2009 Frederik Himpe <fhimpe@mandriva.org> 9.8.1-1mdv2010.0
+ Revision: 411752
- update to new version 9.8.1

* Thu Jul 16 2009 Paulo Andrade <pcpa@mandriva.com.br> 9.7.1-1mdv2010.0
+ Revision: 396514
- Update to latest upstream release.

* Sat Sep 27 2008 Oden Eriksson <oeriksson@mandriva.com> 0.9j-6mdv2009.0
+ Revision: 288910
- rebuild

* Thu Jul 24 2008 Thierry Vignaud <tv@mandriva.org> 0.9j-5mdv2009.0
+ Revision: 244623
- rebuild

* Sat Feb 02 2008 Frederik Himpe <fhimpe@mandriva.org> 0.9j-3mdv2008.1
+ Revision: 161541
- Really fix ecl-doc requirement

* Sat Feb 02 2008 Frederik Himpe <fhimpe@mandriva.org> 0.9j-2mdv2008.1
+ Revision: 161480
- Fix requirements of doc package

* Sat Feb 02 2008 Frederik Himpe <fhimpe@mandriva.org> 0.9j-1mdv2008.1
+ Revision: 161459
- import ecl


