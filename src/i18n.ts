export const LANGS = ["vi", "en"] as const;
export type Lang = (typeof LANGS)[number];

export const DEFAULT_LANG: Lang = "vi";

/** Ngôn ngữ đã có nội dung thật. Thêm "en" vào đây khi bản dịch sẵn sàng. */
export const ACTIVE_LANGS: Lang[] = ["vi"];

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
    siteTitle: "Engineering Lessons — ghi chép kỹ thuật về những hệ thống đã xây",
    siteDescription:
      "Loạt bài về các hệ thống học máy đã từng xây: cách tiếp cận, đối chiếu với chuẩn ngành, và những bài học rút ra.",
    navPosts: "Bài viết",
    navAbout: "Giới thiệu",
    toggleTheme: "Sáng / Tối",
    inThisPost: "Trong bài",
    prevPost: "Bài trước",
    nextPost: "Bài sau",
    footer: "Ghi chép kỹ thuật về những hệ thống đã từng xây.",
  },
  en: {
    siteTitle: "Engineering Lessons — notes on systems I have built",
    siteDescription:
      "Essays on machine learning systems built over the years: the approach taken, how the industry does it, and what stayed useful afterwards.",
    navPosts: "Posts",
    navAbout: "About",
    toggleTheme: "Light / Dark",
    inThisPost: "In this post",
    prevPost: "Previous",
    nextPost: "Next",
    footer: "Engineering notes on systems built over the years.",
  },
};
