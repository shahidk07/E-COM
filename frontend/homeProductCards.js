const productContainer =document.querySelector("#productcontainer");
const productTemplate = document.querySelector("#productTemplate");



export const showProductContainer = (products) =>
{
    if(!products)
    {
        return false;
    }   
    //destructure
    products.forEach((curElem) =>{
        const {id,name,image,price} = curElem;

            //clone product inside template
    const productClone = document.importNode(productTemplate.content,true);
    productClone.querySelector('#productname').textContent = name;
    productContainer.append(productClone);
    } );
};