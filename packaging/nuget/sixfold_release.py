#!/usr/bin/env python3
#
#
# NuGet release packaging tool for Sixfold.
# Creates a NuGet package from CI artifacts.
#

import sys
import argparse
import packaging
import sixfold_packaging

dry_run = False

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",
                        help="Locate artifacts but don't build anything",
                        action="store_true")
    parser.add_argument("--directory", help="Download directory", default="dl-6f")
    parser.add_argument("--no-cleanup", help="Don't clean up temporary folders", action="store_true")
    parser.add_argument("--nuget-version", help="The nuget package version", default=None)
    parser.add_argument("--class", help="Packaging class (see packaging.py)", default="NugetPackage", dest="pkgclass")

    args = parser.parse_args()
    dry_run = args.dry_run

    match = {'tag': '6f'}

    pkgclass = getattr(sixfold_packaging, args.pkgclass)

    try:
        match.update(getattr(pkgclass, 'match'))
    except:
        pass

    arts = packaging.Artifacts(match, args.directory)

    # Collect common local artifacts, such as support files.
    arts.collect_local('common', req_tag=False)

    while True:
        arts.collect_local(arts.dlpath)

        if len(arts.artifacts) == 0:
            raise ValueError('No artifacts found for %s' % match)

        print('Collected artifacts (%s):' % (arts.dlpath))
        for a in arts.artifacts:
            print(' %s' % a.lpath)
        print('')

        package_version = args.nuget_version

        print('')

        if dry_run:
            sys.exit(0)

        print('Building packages:')

        try:
            p = pkgclass(package_version, arts)
            pkgfile = p.build(buildtype='release')
            break
        except packaging.MissingArtifactError as e:
            raise e

    print('')

    if not args.no_cleanup:
        p.cleanup()
    else:
        print(' --no-cleanup: leaving %s' % p.stpath)

    if not p.verify(pkgfile):
        print('Package failed verification.')
        sys.exit(1)

    print('Created package: %s' % pkgfile)
