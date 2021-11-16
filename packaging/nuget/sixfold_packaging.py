#!/usr/bin/env python3
#
# NuGet packaging script.
#


import os
import sys
import tempfile
import shutil
import subprocess
import packaging
from fnmatch import fnmatch
from zfile import zfile

if sys.version_info[0] < 3:
    from urllib import unquote
else:
    from urllib.parse import unquote

dry_run = False


class NugetPackage(packaging.Package):
    """ All platforms, archs, et.al, are bundled into one set of
        NuGet output packages: "main", redist and symbols """

    def __init__(self, version, arts):
        if version.startswith('v'):
            version = version[1:]  # Strip v prefix
        super(NugetPackage, self).__init__(version, arts, "nuget")

    def cleanup(self):
        if os.path.isdir(self.stpath):
            shutil.rmtree(self.stpath)

    def build(self, buildtype):
        """ Build single NuGet package for all its artifacts. """

        # NuGet removes the prefixing v from the version.
        vless_version = self.kv['version']
        if vless_version[0] == 'v':
            vless_version = vless_version[1:]

        self.stpath = tempfile.mkdtemp(prefix="out-", suffix="-%s" % buildtype,
                                       dir=".")

        self.render('librdkafka.redist.nuspec')
        self.copy_template('librdkafka.redist.targets',
                           destpath=os.path.join('build', 'native'))
        self.copy_template('librdkafka.redist.props',
                           destpath='build')
        for f in ['../../README.md', '../../CONFIGURATION.md', '../../LICENSES.txt']:
            shutil.copy(f, self.stpath)

        # Generate template tokens for artifacts
        for a in self.arts.artifacts:
            if 'bldtype' not in a.info:
                a.info['bldtype'] = 'release'

            a.info['variant'] = '%s-%s-%s' % (a.info.get('plat'),
                                              a.info.get('arch'),
                                              a.info.get('bldtype'))
            if 'toolset' not in a.info:
                a.info['toolset'] = 'v120'

        mappings = [
            # Common Win runtime
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'msvcr120.zip'}, 'msvcr120.dll',
             'runtimes/win-x64/native/msvcr120.dll'],
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'msvcr120.zip'}, 'msvcp120.dll',
             'runtimes/win-x64/native/msvcp120.dll'],

            # matches librdkafka.redist.{VER}.nupkg
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka.redist*'},
             'build/native/bin/v120/x64/Release/librdkafka.dll', 'runtimes/win-x64/native/librdkafka.dll'],
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka.redist*'},
             'build/native/bin/v120/x64/Release/librdkafkacpp.dll', 'runtimes/win-x64/native/librdkafkacpp.dll'],
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka.redist*'},
             'build/native/bin/v120/x64/Release/zlib.dll', 'runtimes/win-x64/native/zlib.dll'],
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka.redist*'},
             'build/native/bin/v120/x64/Release/libzstd.dll', 'runtimes/win-x64/native/libzstd.dll'],
            # matches librdkafka.{VER}.nupkg
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka*', 'fname_excludes': ['redist', 'symbols']},
             'build/native/lib/v120/x64/Release/librdkafka.lib',
             'build/native/lib/win/x64/win-x64-Release/v120/librdkafka.lib'],
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka*', 'fname_excludes': ['redist', 'symbols']},
             'build/native/lib/v120/x64/Release/librdkafkacpp.lib',
             'build/native/lib/win/x64/win-x64-Release/v120/librdkafkacpp.lib'],

            # Header files
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka*', 'fname_excludes': ['redist', 'symbols']},
             'build/native/include/librdkafka/rdkafka.h', 'build/native/include/librdkafka/rdkafka.h'],
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka*', 'fname_excludes': ['redist', 'symbols']},
             'build/native/include/librdkafka/rdkafkacpp.h', 'build/native/include/librdkafka/rdkafkacpp.h'],
            [{'arch': 'x64', 'plat': 'win', 'fname_glob': 'librdkafka*', 'fname_excludes': ['redist', 'symbols']},
             'build/native/include/librdkafka/rdkafka_mock.h', 'build/native/include/librdkafka/rdkafka_mock.h'],

            # Common Win runtime
            [{'arch': 'x86', 'plat': 'win', 'fname_glob': 'msvcr120.zip'}, 'msvcr120.dll',
             'runtimes/win-x86/native/msvcr120.dll'],
            [{'arch': 'x86', 'plat': 'win', 'fname_glob': 'msvcr120.zip'}, 'msvcp120.dll',
             'runtimes/win-x86/native/msvcp120.dll'],

            # matches librdkafka.redist.{VER}.nupkg
            [{'arch': 'x86', 'plat': 'win', 'fname_glob': 'librdkafka.redist*'},
             'build/native/bin/v120/Win32/Release/librdkafka.dll', 'runtimes/win-x86/native/librdkafka.dll'],
            [{'arch': 'x86', 'plat': 'win', 'fname_glob': 'librdkafka.redist*'},
             'build/native/bin/v120/Win32/Release/librdkafkacpp.dll', 'runtimes/win-x86/native/librdkafkacpp.dll'],
            [{'arch': 'x86', 'plat': 'win', 'fname_glob': 'librdkafka.redist*'},
             'build/native/bin/v120/Win32/Release/zlib.dll', 'runtimes/win-x86/native/zlib.dll'],
            [{'arch': 'x86', 'plat': 'win', 'fname_glob': 'librdkafka.redist*'},
             'build/native/bin/v120/Win32/Release/libzstd.dll', 'runtimes/win-x86/native/libzstd.dll'],

            # matches librdkafka.{VER}.nupkg
            [{'arch': 'x86', 'plat': 'win', 'fname_glob': 'librdkafka*', 'fname_excludes': ['redist', 'symbols']},
             'build/native/lib/v120/Win32/Release/librdkafka.lib',
             'build/native/lib/win/x86/win-x86-Release/v120/librdkafka.lib'],
            [{'arch': 'x86', 'plat': 'win', 'fname_glob': 'librdkafka*', 'fname_excludes': ['redist', 'symbols']},
             'build/native/lib/v120/Win32/Release/librdkafkacpp.lib',
             'build/native/lib/win/x86/win-x86-Release/v120/librdkafkacpp.lib']
        ]

        for m in mappings:
            attributes = m[0]
            fname_glob = attributes['fname_glob']
            del attributes['fname_glob']
            fname_excludes = []
            if 'fname_excludes' in attributes:
                fname_excludes = attributes['fname_excludes']
                del attributes['fname_excludes']

            artifact = None
            for a in self.arts.artifacts:
                found = True

                for attr in attributes:
                    if a.info[attr] != attributes[attr]:
                        found = False
                        break

                if not fnmatch(a.fname, fname_glob):
                    found = False

                for exclude in fname_excludes:
                    if exclude in a.fname:
                        found = False
                        break

                if found:
                    artifact = a
                    break

            if artifact is None:
                raise packaging.MissingArtifactError(
                    'unable to find artifact with tags %s matching "%s"' % (str(attributes), fname_glob))

            outf = os.path.join(self.stpath, m[2])
            member = m[1]
            try:
                zfile.ZFile.extract(artifact.lpath, member, outf)
            except KeyError as e:
                raise Exception('file not found in archive %s: %s. Files in archive are: %s' % (
                    artifact.lpath, e, zfile.ZFile(artifact.lpath).getnames()))

        print('Tree extracted to %s' % self.stpath)

        # After creating a bare-bone nupkg layout containing the artifacts
        # and some spec and props files, call the 'nuget' utility to
        # make a proper nupkg of it (with all the metadata files).
        subprocess.check_call("nuget pack %s -BasePath %s -NonInteractive" % (os.path.join(self.stpath, 'librdkafka.redist.nuspec'), self.stpath), shell=True)

        return 'librdkafka.redist.%s.nupkg' % vless_version

    def verify(self, path):
        """ Verify package """
        expect = [
            "librdkafka.redist.nuspec",
            "LICENSES.txt",
            "build/librdkafka.redist.props",
            "build/native/librdkafka.redist.targets",
            "build/native/include/librdkafka/rdkafka.h",
            "build/native/include/librdkafka/rdkafkacpp.h",
            "build/native/include/librdkafka/rdkafka_mock.h",
            "build/native/lib/win/x64/win-x64-Release/v120/librdkafka.lib",
            "build/native/lib/win/x64/win-x64-Release/v120/librdkafkacpp.lib",
            "build/native/lib/win/x86/win-x86-Release/v120/librdkafka.lib",
            "build/native/lib/win/x86/win-x86-Release/v120/librdkafkacpp.lib",
            "runtimes/win-x64/native/librdkafka.dll",
            "runtimes/win-x64/native/librdkafkacpp.dll",
            "runtimes/win-x64/native/msvcr120.dll",
            "runtimes/win-x64/native/msvcp120.dll",
            "runtimes/win-x64/native/zlib.dll",
            "runtimes/win-x64/native/libzstd.dll",
            "runtimes/win-x86/native/librdkafka.dll",
            "runtimes/win-x86/native/librdkafkacpp.dll",
            "runtimes/win-x86/native/msvcr120.dll",
            "runtimes/win-x86/native/msvcp120.dll",
            "runtimes/win-x86/native/zlib.dll",
            "runtimes/win-x86/native/libzstd.dll"]

        missing = list()
        with zfile.ZFile(path, 'r') as zf:
            print('Verifying %s:' % path)

            # Zipfiles may url-encode filenames, unquote them before matching.
            pkgd = [unquote(x) for x in zf.getnames()]
            missing = [x for x in expect if x not in pkgd]

        if len(missing) > 0:
            print('Missing files in package %s:\n%s' % (path, '\n'.join(missing)))
            return False
        else:
            print('OK - %d expected files found' % len(expect))
            return True
