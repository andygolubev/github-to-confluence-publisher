# Folder and page hierarchy

The publisher mirrors **directory structure** under the configured Markdown root. Folder names become **Confluence page titles**; only files ending in `.md` become content pages.

## Mapping rules

![Repository tree mirrored under Confluence parent](/data_images/folder-to-space-mapping.svg)

| On disk | In Confluence |
|---------|----------------|
| Subfolder | Child page with **Children** macro; new parent for nested content |
| `Something.md` | Page titled **`Something.md`** (full filename including extension) |
| `readme.png`, `notes.txt` | Ignored for publish (not Markdown) |

### Ordering note

`os.scandir` order is **filesystem-dependent**. Do not rely on Confluence child order matching lexical sort unless your environment guarantees ordering; use numeric prefixes in folder and file names if you need stable ordering (as in this example tree).

## Children Display macro

Folder pages exist mainly as **navigation shells**: their body is the Confluence **Children** macro so readers see up-to-date descendants without maintaining manual links.

## Parent page

The **configured parent** is not created by the tool — you create it once in Confluence and put its ID in config. All generated pages (folders + Markdown) hang under that parent or its descendants.
