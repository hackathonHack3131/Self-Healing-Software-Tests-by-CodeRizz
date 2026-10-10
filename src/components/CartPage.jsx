import React from 'react';
import { useDemo } from '../context/DemoContext';
import {
  Trash2,
  ArrowLeft,
  ArrowRight,
  ShoppingBag,
  ShieldCheck,
  Tag,
  CreditCard
} from 'lucide-react';

export const CartPage = () => {
  const {
    cartItems,
    cartSubtotal,
    totalCartCount,
    updateQuantity,
    removeFromCart,
    setView,
    checkoutButtonId,
    checkoutButtonLabel,
    isRearrangedLayout,
    isRenamedSelectors
  } = useDemo();

  const handleCheckoutNavigation = () => {
    if (cartItems.length > 0) {
      setView('checkout');
    }
  };

  if (cartItems.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <div className="bg-white rounded-3xl p-10 border border-slate-200/90 shadow-sm space-y-5">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto text-slate-400">
            <ShoppingBag className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Your Cart is Empty</h2>
          <p className="text-sm text-slate-500 max-w-md mx-auto">
            You don't have any items in your cart yet. Explore our performance running sneakers to test the checkout workflow.
          </p>
          <div>
            <button
              type="button"
              id="continue-shopping-empty-btn"
              onClick={() => setView('product')}
              className="px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-sm font-semibold transition-smooth inline-flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Explore Sneakers</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render Version B: Rearranged Layout
  if (isRearrangedLayout) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12" data-layout="redesigned-b">
        {/* Version B Header Banner */}
        <div className="mb-6 p-4 rounded-2xl bg-gradient-to-r from-indigo-900 via-slate-900 to-cyan-900 text-white flex flex-wrap items-center justify-between gap-4 shadow-md">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-500/20 rounded-xl border border-indigo-400/30">
              <CreditCard className="w-5 h-5 text-indigo-300" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-bold">Shopping Cart (vB Redesign)</h1>
                <span className="text-[10px] font-mono bg-indigo-500/30 text-indigo-200 px-2 py-0.5 rounded-full uppercase tracking-wider">
                  Layout Altered
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Summary is prominently prioritized with relocated checkout trigger.
              </p>
            </div>
          </div>

          {/* Version B: Prominent Top Action Button */}
          <button
            type="button"
            id={checkoutButtonId}
            onClick={handleCheckoutNavigation}
            className="px-6 py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-cyan-400 to-indigo-400 hover:from-cyan-300 hover:to-indigo-300 text-slate-950 shadow-lg shadow-cyan-500/20 transition-all active:scale-95 flex items-center space-x-2"
          >
            <span>{checkoutButtonLabel}</span>
            <ArrowRight className="w-4 h-4 text-slate-950" />
          </button>
        </div>

        {/* 2-Column Grid (Summary First on Desktop, Items List on Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Version B: Order Summary Card (Left Column) */}
          <div className="lg:col-span-5 order-1 lg:order-1 space-y-4">
            <div className="bg-white rounded-3xl p-6 border-2 border-indigo-100 shadow-lg space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <h2 className="text-base font-bold text-slate-900">Cart Total & Breakdown</h2>
                <span className="text-xs font-mono font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-lg">
                  {totalCartCount} item(s)
                </span>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between text-slate-600">
                  <span>Cart Subtotal</span>
                  <span className="font-semibold text-slate-900">₹{cartSubtotal.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Shipping Fee</span>
                  <span className="text-emerald-600 font-semibold uppercase text-xs">FREE EXPRESS</span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Applicable GST (18%)</span>
                  <span className="text-slate-500 text-xs">Included</span>
                </div>
                <div className="pt-3 border-t border-slate-100 flex justify-between items-baseline">
                  <span className="text-base font-bold text-slate-900">Payable Total</span>
                  <span className="text-2xl font-black text-indigo-700 font-mono">
                    ₹{cartSubtotal.toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Version B Bottom Secondary Button */}
              <button
                type="button"
                id="continue-shopping-btn"
                onClick={() => setView('product')}
                className="w-full py-3 rounded-xl font-semibold text-xs text-slate-700 bg-slate-100 hover:bg-slate-200 transition-smooth flex items-center justify-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4 text-slate-600" />
                <span>Continue Shopping</span>
              </button>
            </div>

            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200 text-xs text-slate-500 flex items-center space-x-3">
              <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0" />
              <span>Simulated e-commerce environment ready for HealTest autonomous self-healing Playwright validation.</span>
            </div>
          </div>

          {/* Version B: Cart Items List (Right Column) */}
          <div className="lg:col-span-7 order-2 lg:order-2 space-y-4">
            <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm space-y-4">
              <h2 className="text-base font-bold text-slate-900 pb-3 border-b border-slate-100">
                Selected Products
              </h2>

              <div className="divide-y divide-slate-100">
                {cartItems.map((item) => (
                  <div key={`${item.id}-${item.size}`} className="py-4 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                    <div className="flex items-center space-x-4">
                      <div className="w-20 h-20 rounded-2xl bg-slate-100 p-2 shrink-0 border border-slate-200 overflow-hidden">
                        <img src={item.image} alt={item.name} className="w-full h-full object-contain" />
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-slate-900">{item.name}</h3>
                        <p className="text-xs text-slate-500 mt-0.5">Size: <span className="font-semibold text-slate-800">{item.size}</span></p>
                        <p className="text-sm font-bold text-indigo-600 font-mono mt-1">₹{item.price.toLocaleString()}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="flex items-center border border-slate-300 rounded-xl overflow-hidden bg-slate-50">
                        <button
                          type="button"
                          onClick={() => updateQuantity(item.id, item.size, item.quantity - 1)}
                          className="px-2.5 py-1 text-sm font-bold hover:bg-slate-200 transition-smooth"
                        >
                          -
                        </button>
                        <span className="px-3 py-1 font-mono text-xs font-bold min-w-8 text-center">
                          {item.quantity}
                        </span>
                        <button
                          type="button"
                          onClick={() => updateQuantity(item.id, item.size, item.quantity + 1)}
                          className="px-2.5 py-1 text-sm font-bold hover:bg-slate-200 transition-smooth"
                        >
                          +
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={() => removeFromCart(item.id, item.size)}
                        className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-smooth"
                        title="Remove item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Render Version A: Baseline Layout
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12" data-layout="baseline-a">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-950 tracking-tight">
            Shopping Cart
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Review your items and proceed to secure checkout
          </p>
        </div>
        <button
          type="button"
          id="continue-shopping-btn"
          onClick={() => setView('product')}
          className="text-xs font-semibold text-cyan-700 hover:text-cyan-800 hover:underline flex items-center space-x-1"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Continue Shopping</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Cart Items List */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm">
            <div className="divide-y divide-slate-100">
              {cartItems.map((item) => (
                <div
                  key={`${item.id}-${item.size}`}
                  className="py-5 first:pt-0 last:pb-0 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-20 h-20 rounded-2xl bg-slate-100 p-2 shrink-0 border border-slate-200/80 overflow-hidden">
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-full h-full object-contain"
                      />
                    </div>
                    <div>
                      <h2 className="font-bold text-base text-slate-900">{item.name}</h2>
                      <div className="flex items-center space-x-3 text-xs text-slate-500 mt-1">
                        <span>Size: <strong className="text-slate-800">{item.size}</strong></span>
                        <span>•</span>
                        <span className="text-emerald-600 font-medium">In Stock</span>
                      </div>
                      <p className="text-sm font-bold text-slate-900 font-mono mt-1.5">
                        ₹{item.price.toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between sm:justify-end space-x-4">
                    {/* Quantity Selector */}
                    <div className="flex items-center border border-slate-300 rounded-xl overflow-hidden bg-white shadow-2xs">
                      <button
                        type="button"
                        id={`cart-decrease-${item.id}`}
                        onClick={() => updateQuantity(item.id, item.size, item.quantity - 1)}
                        className="px-3 py-1.5 font-bold text-slate-700 hover:bg-slate-100 transition-smooth"
                      >
                        -
                      </button>
                      <span className="px-3.5 py-1.5 font-mono text-xs font-bold min-w-8 text-center text-slate-900">
                        {item.quantity}
                      </span>
                      <button
                        type="button"
                        id={`cart-increase-${item.id}`}
                        onClick={() => updateQuantity(item.id, item.size, item.quantity + 1)}
                        className="px-3 py-1.5 font-bold text-slate-700 hover:bg-slate-100 transition-smooth"
                      >
                        +
                      </button>
                    </div>

                    {/* Subtotal for Item */}
                    <span className="font-mono font-bold text-sm text-slate-900 min-w-16 text-right hidden sm:block">
                      ₹{(item.price * item.quantity).toLocaleString()}
                    </span>

                    {/* Remove button */}
                    <button
                      type="button"
                      id={`cart-remove-${item.id}`}
                      onClick={() => removeFromCart(item.id, item.size)}
                      className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-smooth"
                      title="Remove item"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Order Summary Card (Version A Baseline) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm space-y-5">
            <h2 className="text-lg font-bold text-slate-900 pb-3 border-b border-slate-100">
              Order Summary
            </h2>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between text-slate-600">
                <span>Subtotal ({totalCartCount} items)</span>
                <span className="font-semibold text-slate-900">₹{cartSubtotal.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Estimated Delivery</span>
                <span className="text-emerald-600 font-semibold uppercase text-xs">Free</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Taxes & Duties</span>
                <span className="text-slate-500 text-xs">₹0.00</span>
              </div>
              <div className="pt-3 border-t border-slate-100 flex justify-between items-baseline">
                <span className="text-base font-bold text-slate-900">Total</span>
                <span id="cart-total-amount" className="text-2xl font-black text-slate-950 font-mono">
                  ₹{cartSubtotal.toLocaleString()}
                </span>
              </div>
            </div>

            {/* Version A Baseline Checkout Button (Positioned at bottom of summary card) */}
            <button
              type="button"
              id={checkoutButtonId}
              onClick={handleCheckoutNavigation}
              className="w-full py-4 rounded-2xl font-bold text-sm bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20 transition-all active:scale-98 flex items-center justify-center space-x-2"
            >
              <span>{checkoutButtonLabel}</span>
              <ArrowRight className="w-4 h-4 text-slate-950" />
            </button>
          </div>

          <div className="bg-white rounded-2xl p-4 border border-slate-200/80 text-xs text-slate-500 flex items-center space-x-3">
            <ShieldCheck className="w-5 h-5 text-cyan-600 shrink-0" />
            <span>Encrypted checkout. Simulated data only for HealTest AI automated evaluation.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
