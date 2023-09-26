import json
import re

js_code = """
    if (item == null) {
      var _learnq = _learnq || [];
      var item = {
        Name: "KAN CAN Emma High-Rise Mom Jeans - Light Wash",
        ProductID: 7243874467876,
        Categories: ["Bottoms","Jeans","New Arrivals"],
        ImageURL: "https://cdn.shopify.com/s/files/1/0191/0188/products/CCB0207223-0656_grande.jpg?v=1676141983",
        URL: "https://www.closetcandy.com/products/kan-can-emma-high-rise-mom-jeans-light-wash",
        Brand: "KC",
        Price: "$59.00",
        CompareAtPrice: "$0.00"
      };
      _learnq.push(['track', 'Viewed Product', item]);
      _learnq.push(['trackViewedItem', {
        Title: item.Name,
        ItemId: item.ProductID,
        Categories: item.Categories,
        ImageUrl: item.ImageURL,
        Url: item.URL,
        Metadata: {
          Brand: item.Brand,
          Price: item.Price,
          CompareAtPrice: item.CompareAtPrice
        }
      }]);
    }
"""

match = re.search(r'var item = ({.*?});', js_code, re.DOTALL)

if match:
    json_str = match.group(1)

    # Replace keys without quotes with keys with quotes
    json_str = re.sub(r'(\b\w+\b)(:)', r'"\1"\2', json_str).replace('""https"', '"https')

    print(json_str)

    data = json.loads(json_str)
    print(data)
else:
    print("No match found.")
