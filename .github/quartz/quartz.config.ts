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
        header: "Schibsted Grotesk",
        body: "Source Sans Pro",
        code: "IBM Plex Mono",
      },
      colors: {
        lightMode: {
          light: "#1e1e1e",
          lightgray: "#2e2e2e",
          gray: "#646464",
          darkgray: "#dadada",
          dark: "#ebebec",
          secondary: "#e0a526",
          tertiary: "#f0c040",
          highlight: "rgba(224, 165, 38, 0.12)",
          textHighlight: "rgba(224, 165, 38, 0.3)",
        },
        darkMode: {
          light: "#1e1e1e",
          lightgray: "#2e2e2e",
          gray: "#646464",
          darkgray: "#dadada",
          dark: "#ebebec",
          secondary: "#e0a526",
          tertiary: "#f0c040",
          highlight: "rgba(224, 165, 38, 0.12)",
          textHighlight: "rgba(224, 165, 38, 0.3)",
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
          light: "github-dark",
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
