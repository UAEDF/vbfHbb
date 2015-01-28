find . -maxdepth 1 -not -name \*.out -and -not -name \*.log -type f -exec grep -rnH "POL1-POL2" {} \;
