INSERT INTO adherents (nom, prenom, mail, login, password, date_de_depart, datesignedminet, mailinglist)
SELECT 'Admin', 'Dev', 'admin@adh6.local', 'admin', '209c6174da490caeb422f3fa5a7ae634',
       DATE_ADD(CURDATE(), INTERVAL 1 YEAR), NOW(), 0
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM adherents WHERE login = 'admin');

INSERT INTO adherents (nom, prenom, mail, login, password, date_de_depart, datesignedminet, mailinglist)
SELECT 'Adherent', 'Dev', 'adherent@adh6.local', 'adherent', '6d6b39f67d87d20f851558a3a69de569',
       DATE_ADD(CURDATE(), INTERVAL 1 YEAR), NOW(), 0
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM adherents WHERE login = 'adherent');

INSERT INTO vlans (numero, adresses, adressesv6)
SELECT 42, '192.168.42.0/24', 'fe80:42::/64'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM vlans WHERE numero = 42);

INSERT INTO chambres (numero, description, vlan_id)
SELECT 1234, 'Chambre de dev', (SELECT id FROM vlans WHERE numero = 42)
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM chambres WHERE numero = 1234);

INSERT IGNORE INTO rooms_members_association (room_id, member_id)
SELECT c.id, a.id FROM chambres c JOIN adherents a ON a.login = 'adherent' WHERE c.numero = 1234;

UPDATE adherents
SET chambre_id = (SELECT id FROM chambres WHERE numero = 1234)
WHERE login = 'adherent' AND chambre_id IS NULL;

INSERT INTO devices (mac, ip, adherent_id, type, name)
SELECT '02-00-00-00-12-34', '192.168.42.2', a.id, 0, 'PC de dev'
FROM adherents a
WHERE a.login = 'adherent'
  AND NOT EXISTS (SELECT 1 FROM devices WHERE mac = '02-00-00-00-12-34');

INSERT INTO switches (description, ip, communaute)
SELECT 'Switch de dev', 'snmpsim', 'adh6'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM switches WHERE ip = 'snmpsim');

INSERT INTO ports (numero, oid, switch_id, chambre_id)
SELECT '0/0/1', '10101', s.id, (SELECT id FROM chambres WHERE numero = 1234)
FROM switches s
WHERE s.ip = 'snmpsim'
  AND NOT EXISTS (SELECT 1 FROM ports p WHERE p.switch_id = s.id AND p.numero = '0/0/1');

INSERT INTO ports (numero, oid, switch_id, chambre_id)
SELECT '0/0/2', '10102', s.id, NULL
FROM switches s
WHERE s.ip = 'snmpsim'
  AND NOT EXISTS (SELECT 1 FROM ports p WHERE p.switch_id = s.id AND (p.oid = '10102' OR p.numero = '0/0/2'));

-- Moyens de paiement
INSERT INTO payment_methods (name)
SELECT p.name
FROM (SELECT 'Liquide' AS name UNION ALL SELECT 'HelloAsso' UNION ALL SELECT 'Carte Bancaire') p
WHERE NOT EXISTS (SELECT 1 FROM payment_methods m WHERE m.name = p.name);

INSERT INTO membership (uuid, duration, first_time, adherent_id, payment_method_id, status, has_room)
SELECT UUID(), 'ONE_YEAR', 1, a.id, (SELECT id FROM payment_methods WHERE name = 'Liquide'), 'COMPLETE', 1
FROM adherents a
WHERE a.login IN ('admin', 'adherent')
  AND NOT EXISTS (SELECT 1 FROM membership m WHERE m.adherent_id = a.id);

INSERT INTO role_mappings (authentication, identifier, role)
SELECT 'USER', 'admin', r.role
FROM (
    SELECT 'ADMIN_READ' AS role UNION ALL SELECT 'ADMIN_WRITE'
    UNION ALL SELECT 'TRESO_READ' UNION ALL SELECT 'TRESO_WRITE'
    UNION ALL SELECT 'NETWORK_READ' UNION ALL SELECT 'NETWORK_WRITE'
) r
WHERE NOT EXISTS (
    SELECT 1 FROM role_mappings m
    WHERE m.authentication = 'USER' AND m.identifier = 'admin' AND m.role = r.role
);
