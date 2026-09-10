// A tiny inline gray-box SVG data URI — used as an <img> fallback wherever a
// product/cart item has no image. via.placeholder.com (the previous fallback)
// shut down years ago and was silently rendering broken images.
export const PLACEHOLDER_IMAGE =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">' +
    '<rect width="100%" height="100%" fill="#e5e7eb"/>' +
    '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" ' +
    'fill="#9ca3af" font-family="sans-serif" font-size="20">No Image</text>' +
    '</svg>'
  );
