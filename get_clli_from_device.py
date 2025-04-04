

def get_clli_from_device(device_fqdn: str) -> str:
    """Given a FQDN or hostname for a device, extract the CLLI."""
    clli: str = ""

    # TDS Device names for routers will be ATLNGAMQcor51.network.tds.net
    # TDS Device names for switches will be STGRUTFKcen13.network.teldta.com
    # Some anomalies exist like CNTCNHdst51
    hostname = device_fqdn.split('.')[0]
    if len(hostname) == 13:
        clli = hostname[:8]
    elif len(hostname) == 11:
        clli = hostname[:6]
    elif len(hostname) == 16:    # CCW specific
        clli = hostname[:11]
    else:
        print("unknown device hostname length")
    
    return clli.upper()

def get_netbox_site_name(clli: str) -> str:
    """Given a CLLI, return the name used in Netbox."""
    nb_site_dict = {
        'ABDLWIXA': "ABDLWIXA",
        'ALMGNMGM': "ALMGNMGM",
        'ALTONMAF': "ALTONMAF",
        'APPLWI': "APPLWI",
        'ARVDCOLN': "ARVDCOLN",
        'ASHWWIEV': "ASHWWIEV",
        'ATLNGAMQ': "ATLNGAMQ - Atlanta Digital Reality",
        'BENDOR04': "BENDOR04",
        'BENDORYD': "BENDORYD",
        'BHLKWIXA': "BHLKWIXA",
        'BLNHMTUK': "BLNHMTUK",
        'BRTHCOBR': "BRTHCOBR",
        'BUTTMTAZ': "BUTTMTAZ",
        'CDCYUTEZ': "CDCYUTEZ",
        'CHCGILDT': "CHCGILDT - Chicago Equinix",
        'CNCRTNXA': "CNCRTNXA",
        'CRALIDXO': "CRALIDXO",
        'CRLBNMCD': "CRLBNMCD",
        'CRTZCODY': "CRTZCODY",
        'CYTNINXA': "CYTNINXA",
        'DNVVCOHF': "DNVVCOHF - Denver Coresite",
        'DNVRCO26': "DNVRCO26 - Denver Coresite",
        'ENWECOSV': "ENWECOSV",
        'ESPKCOBN': "ESPKCOBN",
        'EUCLWIFG': "EUCLWIFG",
        'FTBGWIIE': "FTBGWIIE",
        'FTCMCOMH': "FTCMCOMH",
        'FTCRCOCM': "FTCRCOCM",
        'GRFLMTTH': "GRFLMTTH",
        'HBBSNMEV': "HBBSNMEV",
        'HLNAMTWP': "HLNAMTWP",
        'KGLDGAXA': "KGLDGAXA",
        'LAPIOR04': "LAPIOR04",
        'LNDNINXA': "LNDNINXA",
        'LNDNTNXA': "LNDNTNXA",
        'LSANCARC': "LSANCARC - Coresite LA1",
        'LSVLNV94': "LSVLNV94",
        'LVRGTNXA': "LVRGTNXA",
        'MDRSORBO': "MDRSORBO",
        'MDSNWIGJ': "MDSNWIGJ - Schroeder Rd Madison",
        'MDSNWIKW': "MDSNWIKW",
        'MDSNWIVU01N': "MDSNWIVU01N",
        'MDTNWIXA': "MDTNWIXA",
        'MNTIMNXA': "MNTIMNXA",
        'MOSNWIXA': "MOSNWIXA",
        'MPLSMNCD': "MPLSMNCD",
        'MRDOIDEO': "MRDOIDEO",
        'MRVINCBT': "MRVINCBT",
        'MSQTNVAP': "MSQTNVAP",
        'MSSLMT19': "MSSLMT19",
        'MTJLTNXA': "MTJLTNXA",
        'NANSMEXA': "NANSMEXA",
        'NWLNNHXA': "NWLNNHXA",
        'NYCMNY83': "NYCMNY83 - NYC2(JFK10)",
        'OLNDCAXA': "OLNDCAXA",
        'PHNXAZ19': "PHNXAZ19",
        'PQLKMNXP': "PQLKMNXP",
        'PRSSTNXA': "PRSSTNXA",
        'PRVLOREK': "PRVLOREK",
        'PTBOINXA': "PTBOINXA",
        'PTLDORPB': "PTLDORPB - Portland Pittock",
        'STGRUTFK': "STGRUTFK",
        'STGRUTUJ': "STGRUTUJ",
        'STTLWAWB': "STTLWAWB - Seattle Equinix",
        'THRVORAB': "THRVORAB",
        'TRCNNMCS': "TRCNNMCS",
        'TWFLIDST': "TWFLIDST",
        'VRNAWI': "VRNAWI",
        'WDPKCOAQ': "WDPKCOAQ",
    }
    return nb_site_dict[clli]


if __name__ == "__main__":
    print(get_clli_from_device("ATLNGAMQcor51.network.tds.net"))
    print(get_clli_from_device("CNTCNHdst51.network.tds.net"))
    print(get_clli_from_device("bogus"))
    print(get_clli_from_device("stgrutfkcen13.network.teldta.com"))
    print(get_clli_from_device("mdsnwigjdst51"))

    print(get_netbox_site_name(get_clli_from_device("atlngamqcor52.network.tds.net")))
    print(get_netbox_site_name(get_clli_from_device("bendoryddst51.network.tds.net")))
    print(get_netbox_site_name(get_clli_from_device("CDCYUTEZcen02.network.teldta.com")))
    print(get_netbox_site_name(get_clli_from_device("MDSNWIVU01Ndst53.network.teldta.com")))
