import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

const config: QuartzConfig = {
  configuration: {
    pageTitle: "Curse of Strahd: Reloaded",
    pageTitleSuffix: " | CoS Reloaded",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-US",
    baseUrl: "bonobomagno.github.io/Curse-of-Strahd-Reloaded-ita/en",
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
          secondary: "#d697e9",
          tertiary: "#d79eff",
          highlight: "rgba(255, 208, 0, 0.15)",
          textHighlight: "rgba(255, 208, 0, 0.4)",
        },
        darkMode: {
          light: "#1e1e1e",
          lightgray: "#2e2e2e",
          gray: "#646464",
          darkgray: "#dadada",
          dark: "#ebebec",
          secondary: "#d697e9",
          tertiary: "#d79eff",
          highlight: "rgba(255, 208, 0, 0.15)",
          textHighlight: "rgba(255, 208, 0, 0.4)",
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
