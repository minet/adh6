# coding=utf-8
import abc
import sqlite3  #on suppose qu"on travaille sur sqlite


class IPAllocator(metaclass=abc.ABCMeta):
    """
    Abstract interface to allocate IP addresses.
    """

    @abc.abstractmethod
  
    base=sqlite3.connect(spec.yaml) #pas encore sur de comment importer la bdd de ADH6

    def adresseUsedNuméroBatiment(NumeroBatiment):
    NumeroBatiment=x
    AdresseUsed=[]
    base=conn.base()
    base.execute("""SELECT ipv4Adress, FROM Device, WHERE ipv4Adress[9]=x""")
    rows=base.fetchall()
    for row in rows:
        AdresseUsed.append('{0} : {1} - {2}'.format(row[0], row[1], row[2])
    return AdresseUsed

   def allocateBatiment(NumeroBatiment):
    
    if NuméroBatiment=1:
        return '157.159.41.0/22', tab1 #on a supposé ca 
    elif NuméroBatiment=2:
        return '157.159.42.0/22'
    elif NuméroBatiment=3:
        return '157.159.43.0/22'
    elif NuméroBatiment=4:
        return '157.159.44.0/22'
    elif NuméroBatiment=5:
        return '157.159.45.0/22'
    elif NuméroBatiment=6:
        return '157.159.46.0/22'
    elif NuméroBatiment=7:
        return '157.159.47.0/22'
    elif NuméroBatiment='Foyer':
        return '157.159.48.0/22'
     #quid des 48 et 49?
    
   def allocate ipv4 (self, ctx, ip_range: str,NumeroBatiment):
    
      x=allocateBatiment(NumeroBatiment) #on a supposé que de les numéros de 40 à 49 correspondaient à un batiment
      domaine = ipaddress.ip_network(x)
      tab=adresseUsedNumeroBatiment(NumeroBatiment)
      for adrr in domaine.hosts():
         if adrr not in tab: 
            return adrr
            
      raise NoMoreIPAvailable
      return 0

       
    @abc.abstractmethod
    def allocate_ip_v6(self, ctx, ip_range: str) -> str:
        """
        Allocates a new unused IP address.

        :raise NoMoreIPAvailable
        """
        pass  # pragma:     no cover

spec.yaml.close()
