#!/bin/bash

mkdir gpg_keys
pkill gpg-agent
for member in president vice-president secretaire tresorier respo-web; do
	export GNUPGHOME="${PWD}/gpg_keys/${member}"
	mkdir $GNUPGHOME
	chmod 700 $GNUPGHOME
	tmpfile=$(mktemp)
	cat > ${tmpfile} <<-EOF
		Key-Type: RSA
		Key-Length: 2048
		Name-Real: Force ${member}
		Name-Email: ${member}@example.com
		Expire-Date: 0
		%no-protection
		%transient-key
		%commit
	EOF
	gpg --quiet --batch --gen-key ${tmpfile}
	chmod -R 600 ${GNUPGHOME}/*
	rm ${tmpfile}
	gpg --quiet --export --armor > ${GNUPGHOME}/../${member}.public.asc
	fp=$(gpg --quiet --with-colons --list-keys "${member}@example.com" | grep fpr | cut -d':' -f10)
	echo "Import this GPG key ${GNUPGHOME}/../${member}.public.asc on the \"key server\""
	echo "And add (or update) this fingerprint ${fp} in the database: \"INSERT INTO bureau_members (name, fp) VALUES (\"${member}\", \"${fp}\");\""
done
unset GNUPGHOME
