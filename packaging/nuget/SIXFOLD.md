# Packaging nupkg files for windows (custom build for Sixfold)

Easiest way to build `librdkafka` from sources would be to use [Appveyor](https://www.appveyor.com/) CI tool.
It has perfect Windows build tools support like Visual Studio 2013, Visual Studio 2015 etc depending which is needed.  

> NOTE: Librdkafka 1.7.0 is built using VS2013 and 1.8.0 with VS2015.

1. Create a free account at Appveyor and connect `librdkafka` repository as a new Appveyor project.
2. Copy [appveyor_vs2013.yml](./appveyor_yamls/appveyor_vs2013.yml) or [appveyor_vs2015.yml](./appveyor_yamls/appveyor_vs2015.yml) to the root of the repo and rename it to `.appveyor.yaml`.
3. On each commit the CI starts and builds artifacts for each job(x86 and x64 architecture). Download & unzip built artifacts to `librdkafka/packaging/nuget/dl-6f` of locally checked out repo. Remember to unzip with the same name as the artifact zip file eg. `p-librdkafka__bld-appveyor__plat-windows__arch-x64__bldtype-Release__tag-6f`. Directories naming is essential as the python script building the `nupkg` package receives information about the architecture, build type etc from the directory name!
4. On windows machine run `python sixfold_release.py --nuget-version <librdkafka version eg. 1.7.0>`. As a result of this you should get new package eg. `librdkafka.redist.1.7.0.nupkg`.
5. Upload this to publicly available `kpi.sixfold.com` bucket: https://console.cloud.google.com/storage/browser/kpi.sixfold.com/librdkafka?project=sixfold-general
6. In [6fold/node-rdkafka](https://github.com/6fold/node-rdkafka/blob/master/package.json#L5) update `librdkafka` version if it was changed so [windows-install.py](https://github.com/6fold/node-rdkafka/blob/master/deps/windows-install.py) can fetch it.
7. On windows machine you can test the build in `6fold/node-rdkafka` repo by running command `node-gyp rebuild`. The latter is the command that is executed as soon as `node-rdkafka` is `yarn add`ed as a project dependency.

There are correct OpenSSL [dependencies](./openssl_vs2013_1.0.2q) attached in case VS2013 build fails to fetch them from Appveyor cache for some reason.  OpenSSL has to be built with the same version of build tools as the `librdkafka` otherwise the build results an error. So the OpenSSL version and the way they are build is essential.
When there's a need to extract them to Appveyor's runner machine `C:\OpenSSL-Win32` and `C:\OpenSSL-Win64` path refer to https://www.appveyor.com/docs/how-to/rdp-to-build-worker/ to easily copy files to the runner machine. Once copied they are cached again so no need to copy again on next build.
