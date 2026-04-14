# Aspera Connect on NoMachine

Source: https://sciwiki.fredhutch.org/compdemos/aspera-on-nx/

## New Installation

1. Start NoMachine session, open Firefox
2. Navigate to https://aspera.fhcrc.org, authenticate
3. Install browser add-on when prompted
4. Download Aspera Connect archive
5. Extract and install:
```bash
tar xvf ibm-aspera-connect-3.11.2.63-linux-g2.12-64.tar.gz
./ibm-aspera-connect-3.11.2.63-linux-g2.12-64.sh
```

## Upgrade

```bash
# Remove old version
rm -r ~/.aspera
# Or relocate
mv .aspera .aspera.no

# Then follow new installation steps (skip add-on)
```

Works similarly with Chromium browser.
