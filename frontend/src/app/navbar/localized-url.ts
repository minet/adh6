export type SupportedLocale = "fr" | "en";

export function localizedUrl(
  pathname: string,
  search: string,
  hash: string,
  locale: SupportedLocale,
): string {
  const pathWithoutLocale = pathname.replace(/^\/(?:fr|en)(?=\/|$)/, "");
  const localizedPath = `/${locale}${pathWithoutLocale || "/"}`;

  return `${localizedPath}${search}${hash}`;
}
