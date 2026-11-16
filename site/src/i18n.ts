export const LANGS = ["vi", "en"] as const;
export type Lang = (typeof LANGS)[number];

export const DEFAULT_LANG: Lang = "vi";
export const ACTIVE_LANGS: Lang[] = ["vi", "en"];

export const LABEL: Record<Lang, string> = {
  vi: "Tiếng Việt",
  en: "English",
};

type Key =
  | "siteTitle"
  | "siteDescription"
  | "navBook"
  | "navCases"
  | "navPaths"
  | "navSearch"
  | "navStatus"
  | "navAbout"
  | "toggleTheme"
  | "inThisPost"
  | "prevPost"
  | "nextPost"
  | "footer"
  | "searchPlaceholder";

export const T: Record<Lang, Record<Key, string>> = {
  vi: {
    siteTitle: "System Craft — sổ tay kiến trúc hệ thống & ghi chép thực chiến",
    siteDescription:
      "Bộ sách kiến trúc hệ thống 145 chương, tầng học thực hành, công cụ tính nhanh và 6 bài phân tích hệ thống học máy đã vận hành.",
    navBook: "Sổ tay (145)",
    navCases: "Case Studies",
    navPaths: "Lộ trình",
    navSearch: "Tìm kiếm",
    navStatus: "Trạng thái",
    navAbout: "Giới thiệu",
    toggleTheme: "Sáng / Tối",
    inThisPost: "Trong bài",
    prevPost: "Bài trước",
    nextPost: "Bài sau",
    footer: "Ghi chép kỹ thuật và sổ tay kiến trúc hệ thống (SA-2028.1).",
    searchPlaceholder: "Tìm nhanh…",
  },
  en: {
    siteTitle: "System Craft — engineering notes and architecture fieldbook",
    siteDescription:
      "Production ML system retrospectives alongside the 145-chapter Systems Atlas technical fieldbook.",
    navBook: "Fieldbook (VI)",
    navCases: "Case Studies",
    navPaths: "Roadmaps (VI)",
    navSearch: "Search",
    navStatus: "Status",
    navAbout: "About",
    toggleTheme: "Light / Dark",
    inThisPost: "In this post",
    prevPost: "Previous",
    nextPost: "Next",
    footer: "Engineering notes and systems architecture fieldbook (SA-2028.1).",
    searchPlaceholder: "Search…",
  },
};
