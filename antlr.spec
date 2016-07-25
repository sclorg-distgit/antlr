%global pkg_name antlr
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

%global debug_package %{nil}
# since we have only a static library

Summary:		ANother Tool for Language Recognition
Name:			%{?scl_prefix}%{pkg_name}
Version:		2.7.7
Release:		29.9%{?dist}
Epoch:			0
License:		Public Domain
URL:			http://www.antlr.org/
Source0:		http://www.antlr2.org/download/antlr-%{version}.tar.gz
Source1:		%{pkg_name}-build.xml
Source2:		%{pkg_name}-script
Source3:                http://repo2.maven.org/maven2/%{pkg_name}/%{pkg_name}/%{version}/%{pkg_name}-%{version}.pom
Patch1:			%{pkg_name}-%{version}-newgcc.patch
# see BZ#848662
Patch2:			antlr-examples-license.patch

%ifarch %ix86 x86_64 ia64 armv4l sparcv9 alpha s390x ppc ppc64
%if ! 0%{?rhel} >= 6
BuildRequires:	mono-core
BuildRequires:	mono-winforms
%endif
%endif
BuildRequires:	%{?scl_prefix}ant
BuildRequires:	%{?scl_prefix}javapackages-tools


%description
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package			tool
Summary:			ANother Tool for Language Recognition
BuildArch:			noarch

%description	tool
ANTLR, ANother Tool for Language Recognition, (formerly PCCTS) is a
language tool that provides a framework for constructing recognizers,
compilers, and translators from grammatical descriptions containing
C++ or Java actions [You can use PCCTS 1.xx to generate C-based
parsers].

%package		manual
Summary:		Manual for %{pkg_name}
BuildArch:		noarch

%description	manual
Documentation for %{pkg_name}.

%package		javadoc
Summary:		Javadoc for %{pkg_name}
BuildArch:		noarch

%description	javadoc
Javadoc for %{pkg_name}.

%package		C++
Summary:		C++ bindings for antlr2 generated parsers

%description	C++
This package provides a static C++ library for parsers generated by ANTLR2.

%package		C++-doc
Summary:		Documentation for C++ bindings for antlr2 generated parsers
BuildRequires:	doxygen
BuildArch:		noarch

%description	C++-doc
This package contains the documentation for the C++ bindings for parsers
generated by ANTLR2.

%prep
%setup -q -n %{pkg_name}-%{version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
# remove all binary libs
find . -name "*.jar" -exec rm -f {} \;
cp -p %{SOURCE1} build.xml
%patch1
%patch2 -p1
# CRLF->LF
sed -i 's/\r//' LICENSE.txt
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
ant -Dj2se.apidoc=%{_javadocdir}/java
cp work/lib/antlr.jar .  # make expects to find it here
export CLASSPATH=.
%configure --without-examples
make CXXFLAGS="${CXXFLAGS} -fPIC" DEBUG=1 verbose=1
rm antlr.jar			 # no longer needed

# fix doc permissions and remove Makefiles
rm doc/{Makefile,Makefile.in}
chmod 0644 doc/*

# generate doxygen docs for C++ bindings
pushd lib/cpp
	doxygen doxygen.cfg
	find gen_doc -type f -exec chmod 0644 {} \;
popd

# build python
cd lib/python
%{__python} setup.py build
cd ../../
%{?scl:EOF}

%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
mkdir -p $RPM_BUILD_ROOT{%{_includedir}/%{pkg_name},%{_libdir},%{_bindir}}

# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p work/lib/%{pkg_name}.jar $RPM_BUILD_ROOT%{_javadir}/%{pkg_name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

# script
install -p -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/antlr

# C++ lib and headers, antlr-config

install -p -m 644 lib/cpp/antlr/*.hpp $RPM_BUILD_ROOT%{_includedir}/%{pkg_name}
install -p -m 644 lib/cpp/src/libantlr.a $RPM_BUILD_ROOT%{_libdir}
install -p -m 755 scripts/antlr-config $RPM_BUILD_ROOT%{_bindir}

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr work/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}

cd ../..

# POM and depmap
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{pkg_name}.pom
%add_maven_depmap -a antlr:antlrall
%{?scl:EOF}

%files tool
%defattr(-,root,root,-)
%doc LICENSE.txt
%{_javadir}/%{pkg_name}*.jar
%{_bindir}/antlr
%{_mavenpomdir}/JPP-%{pkg_name}.pom
%{_mavendepmapfragdir}/%{pkg_name}

# this is actually a development package for the C++ target
# as we ship only a static library, it doesn't make sense
# to have a separate -devel package for the headers
%files C++
%defattr(-,root,root,-)
%{_includedir}/%{pkg_name}
%{_libdir}/libantlr.a
%{_bindir}/antlr-config

%files C++-doc
%defattr(-,root,root,-)
%doc lib/cpp/gen_doc/html/

%files manual
%defattr(-,root,root,-)
%doc doc/*

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}

%changelog
* Mon Jun  2 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-29.9
- Install javadocs to unversioned directory

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-29.8
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-29.7
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-29.6
- Mass rebuild 2014-02-18

* Tue Feb 18 2014 Michal Srb <msrb@redhat.com> - 0:2.7.7-29.5
- Remove python binding

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-29.4
- Remove requires on java

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-29.3
- SCL-ize build-requires

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-29.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-29.1
- First maven30 software collection build

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 02.7.7-29
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 02.7.7-28
- Mass rebuild 2013-12-27

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-27
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.7-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Nov 25 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-25
- Move maven files from C++ to tool subpackage, resolves: rhbz#879885

* Thu Nov  1 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0:2.7.7-24
- Add maven POM

* Sat Aug 18 2012 Miloš Jakubíček <xjakub@fi.muni.cz> - 0:2.7.7-23
- Add patch updating license on ShowString.java and StreamConverter.java
  examples (thanks to Tom Callaway, see BZ#848662)

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.7-22
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Feb 01 2012 Jaroslav Reznik <jreznik@redhat.com> 0:2.7.7-21
- wrong version for jpackage-utils

* Wed Feb 01 2012 Jaroslav Reznik <jreznik@redhat.com> 0:2.7.7-20
- Versioned Java (build)/requires for -tool too

* Mon Jan 30 2012 Jaroslav Reznik <jreznik@redhat.com> 0:2.7.7-19
- Versioned Java (build)/requires

* Fri Jan 27 2012 Alexander Kurtakov <akurtako@redhat.com> 0:2.7.7-18
- Disable c# part for rhel builds.

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.7-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Mar 25 2011 Miloš Jakubíček <xjakub@fi.muni.cz> - 0:2.7.7-16
- Fixed wrong Obsoletes: antlr on antlr-tool (fix #689703)

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.7-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Feb 07 2011 Miloš Jakubíček <xjakub@fi.muni.cz> - 0:2.7.7-14
- Remove INSTALL.txt (fix BZ#661626)
- add python subpackage (fix BZ#505312)

* Mon Feb 07 2011 Miloš Jakubíček <xjakub@fi.muni.cz> - 0:2.7.7-13
- Added missing Obsoletes: antlr on antlr-tool (fix BZ#603466)

* Mon Dec 13 2010 Dan Horák <dan[at]danny.cz> - 0:2.7.7-12
- sync the architecture list in BR with the mono package

* Tue Nov 23 2010 Rex Dieter <rdieter@fedoraproject.org> - 0:2.7.7-11
- -tool: +Requires: java jpackage-utils (#595504)

* Thu Apr 29 2010 Miloš Jakubíček <xjakub@fi.muni.cz> - 0:2.7.7-10
- Use original upstream tarball, prebuilt jars are anyway removed in %%prep
- Don't overuse macros
- Added explanation about headers in the C++ subpackage
- Remove unnecessary Makefile and Makefile.in from %%docs, permissions fixed
- Added doxygen docs for C++ as a -C++-doc subpackage
- antlr-config moved into the C++ subpackage
- Removed %%post and %%postun javadoc relicts from JPackage

* Tue Apr 27 2010 Miloš Jakubíček <xjakub@fi.muni.cz> - 0:2.7.7-9
- Drop native build, alternatives, jedit, gcj bits and other jpackage crap
- Disable debuginfo since we have only a static library.
- Use %%global everywhere
- Split the C++ bindings into a separate -C++ subpackage
- Use -tool subpackage with Provide: antlr to make it possible to be noarch
- Use sed instead of perl => drop BR: perl

* Tue Apr 20 2010 Orion Poplawski <orion@cora.nwra.com> 0:2.7.7-8
- Cannot be noarch

* Wed Apr 7 2010 Alexander Kurtakov <akurtako@redhat.com> 0:2.7.7-7
- Disable gcj.
- Use %%global.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.7-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Mar 20 2009 Deepak Bhole <dbhole@redhat.com> - 0:2.7.7-5
- Include cstdio in CharScanner.hpp (needed to build with GCC 4.4)
- Merge changes from includestrings patch into the above one

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:2.7.7-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 09 2009 Dennis Gilmore <dennis@ausil.us> 2.7.7-3
- exlcude using mono on sparc64

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.7.7-2
- drop repotag

* Wed Feb 27 2008 Deepak Bhole <dbhole@redhat.com> - 0:2.7.7-1jpp.7
- Add strings inclusion (for GCC 4.3)

* Mon Sep 24 2007 Deepak Bhole <dbhole@redhat.com> - 0:2.7.7-1jpp.6
- Resolve bz# 242305: Remove libantlr-pic.a, and compile libantlr.a with fPIC

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 2.7.7-1jpp.5
- Rebuild for selinux ppc32 issue.

* Tue Jun 12 2007 Deepak Bhole <dbhole@redhat.com> 2.7.7-1jpp.4.fc8
- Added a PIC compiled archive (bz# 242305)

* Thu Jun 07 2007 Deepak Bhole <dbhole@redhat.com> 2.7.7-1jpp.3
- Applied patch to fix conditionals (from skasal at redhat dot com)

* Mon Mar 26 2007 Deepak Bhole <dbhole@redhat.com> 2.7.7-1jpp.2
- Added unowned dir to files list

* Fri Jan 19 2007 Deepak Bhole <dbhole@redhat.com> 0:2.7.7-1jpp.1
- Upgrade to 2.7.7
- Resolve 172456 with patches from Vadim Nasardinov and Radu Greab

* Thu Aug 03 2006 Deepak Bhole <dbhole@redhat.com> = 0:2.7.6-4jpp.2
- Add missing postun for javadoc.

* Thu Aug 03 2006 Deepak Bhole <dbhole@redhat.com> = 0:2.7.6-4jpp.1
- Add missing requirements.

* Sat Jul 22 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:2.7.6-3jpp_5fc
- Unstub docs.

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:2.7.6-3jpp_4fc
- Remove hack-libgcj requirement.

* Fri Jul 21 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:2.7.6-3jpp_3fc
- Stub docs. (dist-fc6-java)
- Require hack-libgcj for build. (dist-fc6-java)
- Bump release number.

* Wed Jul 19 2006 Deepak Bhole <dbhole@redhat.com> = 0:2.7.6-3jpp_2fc
- From gbenson@redhat:
- Omit the jedit subpackage to fix dependencies. 

* Wed Jul 19 2006 Deepak Bhole <dbhole@redhat.com> = 0:2.7.6-3jpp_1fc
- Added conditional native compilation.

* Fri Jan 13 2006 Fernando Nasser <fnasser@redhat.com> - 0:2.7.6-2jpp
- First JPP 1.7 build

* Fri Jan 13 2006 Fernando Nasser <fnasser@redhat.com> - 0:2.7.6-1jpp
- Update to 2.7.6.

* Fri Aug 20 2004 Ralph Apel <r.apel at r-apel.de> - 0:2.7.4-2jpp
- Build with ant-1.6.2.
- Made native scripts conditional

* Tue May 18 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:2.7.4-1jpp
- Update to 2.7.4.

* Fri Apr  2 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:2.7.3-2jpp
- Create alternatives also on upgrades.

* Wed Mar 31 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:2.7.3-1jpp
- Update to 2.7.3.
- Include gcj build option and a native subpackage, build using
  "--with native" to get that.
- Add %%{_bindir}/antlr alternative.

* Mon Dec 15 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.7.2-3jpp
- Add non-versioned javadoc dir symlink.
- Crosslink with local J2SE javadocs.
- Spec cleanups, change to UTF-8.

* Sun Mar 30 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:2.7.2-2jpp
- Rebuild for JPackage 1.5.

* Sat Mar  1 2003 Ville Skyttä <ville.skytta at iki.fi> - 2.7.2-1jpp
- Update to 2.7.2.
- Include antlr script and jEdit mode (see antlr-jedit RPM description).
- Use sed instead of bash 2 extension when symlinking jars during build.

* Tue May 07 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.7.1-8jpp
- really section macro
- hardcoded distribution and vendor tag
- group tag again

* Thu May 2 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.7.1-7jpp
- distribution tag
- group tag
- section macro

* Fri Jan 18 2002 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.7.1-6jpp
- versioned dir for javadoc
- no dependencies for manual and javadoc packages
- additional sources in individual archives

* Sat Dec 1 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.7.1-5jpp
- javadoc in javadoc package

* Wed Nov 21 2001 Christian Zoffoli <czoffoli@littlepenguin.org> 2.7.1-4jpp
- removed packager tag
- new jpp extension

* Sat Oct 6 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.7.1-3jpp
- used a build file instead of makefile
- build classes instead of blindly jared them !
- used original tarball
- corrected license spelling

* Sun Sep 30 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.7.1-2jpp
- first unified release
- s/jPackage/JPackage

* Tue Aug 28 2001 Guillaume Rousse <guillomovitch@users.sourceforge.net> 2.7.1-1mdk
- first Mandrake release
