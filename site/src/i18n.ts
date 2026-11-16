export const LANGS = ["vi", "en"] as const;
export type Lang = (typeof LANGS)[number];

export const DEFAULT_LANG: Lang = "vi";

/** Ngôn ngữ đã có nội dung thật. Thêm mã ngôn ngữ vào đây khi bản dịch sẵn sàng. */
export const ACTIVE_LANGS: Lang[] = ["vi", "en"];

export const LABEL: Record<Lang, string> = {
  vi: "Tiếng Việt",
  en: "English",
};

type Key =
  | "siteTitle"
  | "siteDescription"
  | "navPosts"
  | "navAbout"
  | "toggleTheme"
  | "inThisPost"
  | "prevPost"
  | "nextPost"
  | "footer";

export const T: Record<Lang, Record<Key, string>> = {
  vi: {
    siteTitle: "System Craft — ghi chép kỹ thuật và sổ tay kiến trúc hệ thống",
    siteDescription:
      "Loạt bài về các hệ thống học máy đã từng xây: cách tiếp cận, đối chiếu với chuẩn ngành, và những bài học rút ra.",
    navPosts: "Bài viết",
    navAbout: "Giới thiệu",
    toggleTheme: "Sáng / Tối",
    inThisPost: "Trong bài",
    prevPost: "Bài trước",
    nextPost: "Bài sau",
    footer: "Ghi chép kỹ thuật và sổ tay kiến trúc hệ thống.",
  },
  en: {
    siteTitle: "System Craft — engineering notes and architecture fieldbook",
    siteDescription:
      "Notes on machine learning systems that were actually built: how they were put together, how the industry solves the same problems, and what stayed useful afterwards.",
    navPosts: "Posts",
    navAbout: "About",
    toggleTheme: "Light / Dark",
    inThisPost: "In this post",
    prevPost: "Previous",
    nextPost: "Next",
    footer: "Engineering notes on systems built over the years.",
  },
};
