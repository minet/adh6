'use strict';

export const LINKS_LIST = {
  'website': {
    localized: true,
    url: '//www.minet.net/{{lang}}',
    lang: {'fr_FR': 'fr', 'en_US': 'en'}
  },
  'tutorials': {
    localized: true,
    url: '//www.minet.net/{{lang}}/tutoriels.html',
    lang: {'fr_FR': 'fr', 'en_US': 'en'}
  },
  'tickets': {
    localized: true,
    url: '//tickets.minet.net/?lang={{lang}}',
    lang: {'fr_FR': 'fr', 'en_US': 'en_US'}
  },
};

export function localize_link(linkName, lang) {
  const link = LINKS_LIST[linkName];
  if (link.localized) {
    link.url = link.url.replace('{{lang}}', link.lang[lang]);
  }
  return link.url;
}
