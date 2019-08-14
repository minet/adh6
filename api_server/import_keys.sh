#!/bin/bash

echo "Importing public keys into /opt/.gnupg"

gpg --homedir /opt/.gnupg --import gpg_keys/president.public.asc
gpg --homedir /opt/.gnupg --import gpg_keys/vice-president.public.asc
gpg --homedir /opt/.gnupg --import gpg_keys/secretaire.public.asc
gpg --homedir /opt/.gnupg --import gpg_keys/tresorier.public.asc
gpg --homedir /opt/.gnupg --import gpg_keys/respo-web.public.asc

echo "Done"