# Packaging nupkg files for windows (Sixfold)

Easiest way to build `librdkafka` from sources would be to use [Appveyor](https://www.appveyor.com/) CI tool.
It has very good Windows build tools support eg. Visual Studio 2013 or Visual Studio 2015 depending which is needed.
> NOTE: Librdkafka 1.7.0 is built using VS2013 and 1.8.0 with VS2015.

1. Create free account at Appveyor and connect it to `librdkafka` repository.
2. Copy [appveyor_vs2013.yml](./appveyor_yamls/appveyor_vs2013.yml) or [appveyor_vs2015.yml](./appveyor_yamls/appveyor_vs2015.yml) to root of the repo and rename it to `.appveyor.yaml`.
3. On each commit the CI starts and builds artifacts for each job. Download & unzip these artifacts to `librdkafka/packaging/nuget/dl-6f`. Directories naming is essential!
4. On windows machine run `python sixfold_release.py --nuget-version <librdkafka version eg. 1.7.0>`. As a result of this you should get new package eg. `librdkafka.redist.1.7.0.nupkg`.
5. Upload this to publicly available `kpi.sixfold.com` bucket: https://console.cloud.google.com/storage/browser/kpi.sixfold.com/librdkafka?project=sixfold-general
6. In [6fold/node-rdkafka](https://github.com/6fold/node-rdkafka/blob/master/package.json#L5) update `librdkafka` version if it was changed so [windows-install.py](https://github.com/6fold/node-rdkafka/blob/master/deps/windows-install.py) can fetch it.
7. On windows machine you can test the build in `6fold/node-rdkafka` repo by running command `node-gyp rebuild`.

There are correct [dependencies](./openssl_vs2013_1.0.2q) attached in case VS2013 build fails to fetch them for some reason.  
When this happens you need to extract them to `C:\OpenSSL-Win32` and `C:\OpenSSL-Win64` in the Appveyor machine. 
Refer to https://www.appveyor.com/docs/how-to/rdp-to-build-worker/
