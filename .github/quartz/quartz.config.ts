import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

const config: QuartzConfig = {
  configuration: {
    pageTitle: "Curse of Strahd: Reloaded",
    pageTitleSuffix: " | CoS Reloaded ITA",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "it-IT",
    baseUrl: "bonobomagno.github.io/Curse-of-Strahd-Reloaded-ita",
    ignorePatterns: ["private", "templates", ".obsidian", "_other"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Inter",
        body: "Inter",
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          light: "#ffffff",
          lightgray: "#e5e5e5",
          gray: "#b8b8b8",
          darkgray: "#2e3338",
          dark: "#2e3338",
          secondary: "#705dcf",
          tertiary: "#7f6df2",
          highlight: "rgba(127, 109, 242, 0.1)",
          textHighlight: "#fff23688",
        },
        darkMode: {
          light: "#1e1e1e",
          lightgray: "#333333",
          gray: "#646464",
          darkgray: "#dcddde",
          dark: "#dcddde",
          secondary: "#7f6df2",
          tertiary: "#9580ff",
          highlight: "rgba(127, 109, 242, 0.15)",
          textHighlight: "#b3aa0288",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
    ],
  },
}

export default config
