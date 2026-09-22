"""Named setup blocks for the snippets on the site.

Each snippet declares the preamble it needs via `data-setup`. The page shows only
the snippet body; the harness runs preamble + body. This is the same split as a
pytest fixture and the test that requests it.

Catalogs are cone-limited here even though the page shows them whole. The point is
to exercise the API, and some snippets (`gaia.plot_points()`) would try to
materialise a billion rows against the unrestricted catalog.
"""

GAIA = "https://data.lsdb.io/hats/gaia_dr3/gaia"
GAIA_MARGIN = "https://data.lsdb.io/hats/gaia_dr3/gaia_10arcs"
ZTF = "https://data.lsdb.io/hats/ztf_dr14/ztf_object"
ZTF_LC = "https://data.lsdb.io/hats/ztf_dr22/ztf_lc"

CONE = "ra=180.0, dec=10.0, radius_arcsec=600"

PREAMBLES = {
    "none": "import lsdb\n",

    "gaia-loaded": f'''
import matplotlib
matplotlib.use("Agg")
import lsdb
gaia = lsdb.open_catalog("{GAIA}", columns=["ra", "dec", "phot_g_mean_mag"]).cone_search({CONE})
bright = gaia.query("phot_g_mean_mag < 19")
''',

    # The MOC snippets select their own sky, so this one is not cone-limited.
    "gaia-full": f'''
import lsdb
gaia = lsdb.open_catalog("{GAIA}", columns=["ra", "dec", "phot_g_mean_mag"])
''',

    # The table the astropy section builds in the snippet above.
    "astropy-table": '''
import lsdb
from astropy.table import Table
table = Table({
    "ra": [10.0, 20.0, 30.0],
    "dec": [-10.0, -20.0, -30.0],
    "magnitude": [15.0, 16.5, 14.2],
})
''',

    "ztf-loaded": f'''
import lsdb
ztf = lsdb.open_catalog(
    "{ZTF}", columns=["ra", "dec", "ps1_objid", "mean_mag_r"]
).cone_search({CONE})
''',

    "ztf-and-gaia": f'''
import lsdb
ztf = lsdb.open_catalog(
    "{ZTF}", columns=["ra", "dec", "ps1_objid", "mean_mag_r"]
).cone_search({CONE})
gaia = lsdb.open_catalog(
    "{GAIA}", margin_cache="{GAIA_MARGIN}",
    columns=["ra", "dec", "source_id", "phot_g_mean_mag"],
).cone_search({CONE})
''',

    "lc-nested": '''
import lsdb
lc = lsdb.open_catalog(
    "https://data.lsdb.io/hats/alerce",
    columns=["oid", "mean_ra", "mean_dec", "lc"],
)
''',


    # Builds the union MOC that the second MOC snippet reuses.
    "moc": f'''
import lsdb
from functools import reduce
from hats.pixel_math import region_to_moc
gaia = lsdb.open_catalog("{GAIA}", columns=["ra", "dec", "phot_g_mean_mag"])
cone_moc = reduce(
    lambda a, b: a.union(b),
    [region_to_moc.cone_to_moc(ra=r, dec=d, radius_arcsec=4 * 3600, max_depth=10)
     for r, d in [(9.45, -44.02), (150.11, 2.23)]],
)
''',
}
