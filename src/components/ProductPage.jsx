import React, { useState } from 'react';
import { useDemo } from '../context/DemoContext';
import { DEMO_PRODUCT } from '../data/product';
import {
  Star,
  ShoppingBag,
  ArrowRight,
  ShieldCheck,
  Truck,
  RotateCcw,
  Zap,
  Check
} from 'lucide-react';

export const ProductPage = () => {
  const { addToCart, setView, totalCartCount } = useDemo();
  const [selectedSize, setSelectedSize] = useState('UK 9');
  const [quantity, setQuantity] = useState(1);
  const [isAddedFeedback, setIsAddedFeedback] = useState(false);

  const handleAddToCart = () => {
    addToCart(DEMO_PRODUCT, selectedSize, quantity);
    setIsAddedFeedback(true);
    setTimeout(() => {
      setIsAddedFeedback(false);
    }, 1800);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="mb-6 flex items-center space-x-2 text-xs text-slate-500">
        <span>Footwear</span>
        <span>/</span>
        <span>Performance Running</span>
        <span>/</span>
        <span className="text-slate-900 font-semibold">{DEMO_PRODUCT.name}</span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-14 items-start">
        {/* Left Column: Product Visual Showcase */}
        <div className="lg:col-span-7 space-y-4">
          <div className="relative rounded-3xl overflow-hidden bg-gradient-to-b from-slate-100 to-slate-200/70 border border-slate-200/80 shadow-md group">
            {/* Top Badges */}
            <div className="absolute top-4 left-4 z-10 flex flex-wrap gap-2">
              <span className="bg-slate-900 text-white text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-sm">
                Pro Series
              </span>
              <span className="bg-cyan-500 text-slate-950 text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1">
                <Zap className="w-3 h-3" /> 50% OFF
              </span>
            </div>

            {/* Product Image */}
            <div className="aspect-square flex items-center justify-center p-6 sm:p-12 overflow-hidden">
              <img
                id="product-main-image"
                src={DEMO_PRODUCT.image}
                alt={DEMO_PRODUCT.name}
                className="w-full h-full object-contain transform group-hover:scale-105 transition-transform duration-500 ease-out drop-shadow-2xl"
              />
            </div>

            {/* Micro details bar */}
            <div className="bg-white/80 backdrop-blur-md px-6 py-3 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600 font-medium">
              <span>Colorway: Cyan Kinetic Black</span>
              <span className="flex items-center text-emerald-600 font-semibold">
                <span className="w-2 h-2 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                In Stock & Ready to Ship
              </span>
            </div>
          </div>

          {/* Value Props */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-white rounded-2xl p-4 border border-slate-200/70 flex flex-col items-center text-center shadow-2xs">
              <Truck className="w-5 h-5 text-cyan-600 mb-1.5" />
              <span className="text-xs font-bold text-slate-900">Free Express</span>
              <span className="text-[11px] text-slate-500">2-3 Days Delivery</span>
            </div>
            <div className="bg-white rounded-2xl p-4 border border-slate-200/70 flex flex-col items-center text-center shadow-2xs">
              <RotateCcw className="w-5 h-5 text-indigo-600 mb-1.5" />
              <span className="text-xs font-bold text-slate-900">30-Day Returns</span>
              <span className="text-[11px] text-slate-500">Risk-free trial</span>
            </div>
            <div className="bg-white rounded-2xl p-4 border border-slate-200/70 flex flex-col items-center text-center shadow-2xs">
              <ShieldCheck className="w-5 h-5 text-emerald-600 mb-1.5" />
              <span className="text-xs font-bold text-slate-900">100% Authentic</span>
              <span className="text-[11px] text-slate-500">Verified Product</span>
            </div>
          </div>
        </div>

        {/* Right Column: Product Details & Purchase Actions */}
        <div className="lg:col-span-5 space-y-6">
          {/* Header & Title */}
          <div>
            <div className="flex items-center space-x-2 mb-2">
              <div className="flex text-amber-400">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />
                ))}
              </div>
              <span className="text-xs font-bold text-slate-800">{DEMO_PRODUCT.rating}</span>
              <span className="text-xs text-slate-400">({DEMO_PRODUCT.reviewsCount} reviews)</span>
            </div>

            <h1
              id="product-title"
              className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-slate-950 tracking-tight"
            >
              {DEMO_PRODUCT.name}
            </h1>
            <p className="mt-1 text-sm text-slate-600 font-medium">
              {DEMO_PRODUCT.tagline}
            </p>
          </div>

          {/* Pricing Box */}
          <div className="bg-slate-900 rounded-2xl p-5 text-white shadow-lg flex items-baseline justify-between">
            <div>
              <div className="flex items-baseline space-x-3">
                <span id="product-price" className="text-3xl sm:text-4xl font-black text-cyan-400 tracking-tight">
                  ₹{DEMO_PRODUCT.price.toLocaleString()}
                </span>
                <span className="text-base text-slate-400 line-through">
                  ₹{DEMO_PRODUCT.originalPrice.toLocaleString()}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                Inclusive of all taxes & free shipping across India
              </p>
            </div>
            <span className="bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-mono font-semibold px-2.5 py-1 rounded-md">
              Save ₹2,000
            </span>
          </div>

          {/* Description */}
          <div className="text-sm text-slate-600 leading-relaxed bg-white rounded-2xl p-4 border border-slate-200/80">
            <p>{DEMO_PRODUCT.description}</p>
            <ul className="mt-3 space-y-1.5 text-xs text-slate-700">
              {DEMO_PRODUCT.features.map((feat, idx) => (
                <li key={idx} className="flex items-center space-x-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-600"></span>
                  <span>{feat}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Size Selector */}
          <div>
            <div className="flex justify-between items-center mb-2.5">
              <label className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Select Size (UK / India)
              </label>
              <span className="text-xs text-slate-500 font-medium">Size Chart</span>
            </div>
            <div className="grid grid-cols-5 gap-2">
              {DEMO_PRODUCT.sizes.map((size) => {
                const isSelected = selectedSize === size;
                return (
                  <button
                    key={size}
                    type="button"
                    onClick={() => setSelectedSize(size)}
                    className={`py-2.5 rounded-xl font-bold text-xs transition-smooth border ${
                      isSelected
                        ? 'bg-slate-900 text-white border-slate-900 shadow-md ring-2 ring-cyan-500/50'
                        : 'bg-white text-slate-800 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    {size}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Quantity Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider mb-2.5">
              Quantity
            </label>
            <div className="flex items-center space-x-3">
              <div className="flex items-center border border-slate-300 rounded-xl bg-white shadow-2xs overflow-hidden">
                <button
                  type="button"
                  id="decrease-qty-btn"
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-3.5 py-2 font-bold text-slate-700 hover:bg-slate-100 transition-smooth"
                >
                  -
                </button>
                <span
                  id="product-quantity-display"
                  className="px-4 py-2 font-mono font-bold text-sm text-slate-900 min-w-10 text-center"
                >
                  {quantity}
                </span>
                <button
                  type="button"
                  id="increase-qty-btn"
                  onClick={() => setQuantity(quantity + 1)}
                  className="px-3.5 py-2 font-bold text-slate-700 hover:bg-slate-100 transition-smooth"
                >
                  +
                </button>
              </div>
              <span className="text-xs text-slate-500">
                Total: <strong className="text-slate-900">₹{(DEMO_PRODUCT.price * quantity).toLocaleString()}</strong>
              </span>
            </div>
          </div>

          {/* Primary Action Buttons */}
          <div className="space-y-3 pt-2">
            <button
              type="button"
              id="add-to-cart-button"
              onClick={handleAddToCart}
              className={`w-full py-4 rounded-2xl font-bold text-sm tracking-wide transition-all shadow-md active:scale-98 flex items-center justify-center space-x-2 ${
                isAddedFeedback
                  ? 'bg-emerald-600 text-white shadow-emerald-600/30'
                  : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-cyan-500/25'
              }`}
            >
              {isAddedFeedback ? (
                <>
                  <Check className="w-5 h-5 animate-scale-in" />
                  <span>Added to Cart!</span>
                </>
              ) : (
                <>
                  <ShoppingBag className="w-5 h-5 text-slate-950" />
                  <span>Add to Cart — ₹{(DEMO_PRODUCT.price * quantity).toLocaleString()}</span>
                </>
              )}
            </button>

            {/* View Cart Navigation Button */}
            <button
              type="button"
              id="view-cart-button"
              onClick={() => setView('cart')}
              className="w-full py-3.5 rounded-2xl font-bold text-sm bg-white hover:bg-slate-50 text-slate-900 border border-slate-300 transition-smooth flex items-center justify-center space-x-2 hover:border-slate-400"
            >
              <span>View Cart {totalCartCount > 0 ? `(${totalCartCount} items)` : ''}</span>
              <ArrowRight className="w-4 h-4 text-slate-700" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
