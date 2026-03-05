import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

// Custom sort order for top-level folders in the Explorer sidebar
const folderOrder = [
  "Introduction",
  "Chapter 1 - Beginning the Campaign",
  "Chapter 2 - The Land of Barovia",
  "Chapter 3 - Running the Game",
  "Act I - Into the Mists",
  "Act II - The Shadowed Town",
  "Act III - The Broken Land",
  "Act IV - Secrets of the Ancient",
  "Appendices",
]

function explorerSortFn(a: any, b: any): number {
  // Folders (have children) before files (have data)
  const aIsFolder = a.children && a.children.length > 0
  const bIsFolder = b.children && b.children.length > 0
  if (aIsFolder && !bIsFolder) return -1
  if (!aIsFolder && bIsFolder) return 1

  const aName = a.displayName ?? a.slugSegment ?? a.name ?? ""
  const bName = b.displayName ?? b.slugSegment ?? b.name ?? ""
  const aIndex = folderOrder.findIndex((f) => aName.startsWith(f) || f.startsWith(aName))
  const bIndex = folderOrder.findIndex((f) => bName.startsWith(f) || f.startsWith(bName))

  // Both in the ordered list: sort by list position
  if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex
  // Only one in list: listed items first
  if (aIndex !== -1) return -1
  if (bIndex !== -1) return 1
  // Neither in list: alphabetical
  return aName.localeCompare(bName)
}

const explorerOpts = {
  folderClickBehavior: "collapse" as const,
  folderDefaultState: "collapsed" as const,
  sortFn: explorerSortFn,
}

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      "Versione Originale (EN)": "https://www.strahdreloaded.com",
    },
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ArticleTitle(),
    Component.ContentMeta(),
    Component.TagList(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Search(),
    Component.Explorer(explorerOpts),
  ],
  right: [
    Component.DesktopOnly(Component.TableOfContents()),
  ],
}

// components for pages that display lists of pages (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.Breadcrumbs(), Component.ArticleTitle(), Component.ContentMeta()],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Search(),
    Component.Explorer(explorerOpts),
  ],
  right: [],
}
