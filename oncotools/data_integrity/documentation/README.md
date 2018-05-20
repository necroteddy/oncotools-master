# documentation

Documentation is built using Sphinx

# Build
Build documentation as follows:
```bash
cd docs
make html
```

# Update documentation website
Documentation is deployed using the `gh-pages` branch.

Update that branch using:
```bash
git subtree push --prefix docs/_build/html origin gh-pages
```