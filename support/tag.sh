#!/bin/sh

VERSION=`python -c "import avoviirstools; print(avoviirstools.__version__)"`
echo $VERSION
git add avoviirstools/version.py
git commit -m 'version bump'
git push \
&& git tag $VERSION \
&& git push --tags

