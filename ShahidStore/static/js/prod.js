fetch('./productspage.json')
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then((products) => {
    console.log(products); // Log your JSON data
  })
  .catch((error) => {
    console.error('Error fetching JSON:', error);
  });
import {showProductContainer} from "./homeProductsCards";
showProductContainer(products);