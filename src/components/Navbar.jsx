import React from 'react';
import { useDemo } from '../context/DemoContext';
import { ShoppingBag, Sparkles, ShieldCheck } from 'lucide-react';

export const Navbar = () => {
  const { view, setView, totalCartCount, cartSubtotal, version } = useDemo();

  const navSteps = [
    { id: 'product', label: '1. Store' },
    { id: 'cart', label: '2. Cart' },
    { id: 'checkout', label: '3. Checkout' },
    { id: 'confirmation', label: '4. Receipt' }
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 md:top-[74px] z-40 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo & Store Brand */}
          <div className="flex items-center space-x-3">
            <button
              type="button"
              onClick={() => setView('product')}
              className="group flex items-center space-x-2.5 text-left focus:outline-hidden"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-slate-900 via-indigo-950 to-cyan-600 flex items-center justify-center text-white shadow-md shadow-cyan-500/10 group-hover:scale-105 transition-smooth">
                <Sparkles className="w-5 h-5 text-cyan-300" />
              </div>
              <div>
                <div className="flex items-center space-x-1.5">
                  <span className="text-xl font-extrabold tracking-tight text-slate-900">
                    Aura<span className="text-cyan-600">Kicks</span>
                  </span>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200 uppercase tracking-wider font-mono">
                    v{version}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 font-medium">
                  Autonomous Testing Target
                </p>
              </div>
            </button>
          </div>

          {/* Stepper Navigation */}
          <nav aria-label="Shopping Progress" className="hidden md:flex items-center space-x-2">
            {navSteps.map((step, idx) => {
              const isActive = view === step.id;
              return (
                <React.Fragment key={step.id}>
                  <button
                    type="button"
                    onClick={() => {
                      if (step.id === 'product' || step.id === 'cart') {
                        setView(step.id);
                      }
                    }}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-smooth ${
                      isActive
                        ? 'bg-slate-900 text-white shadow-xs'
                        : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
                    }`}
                  >
                    {step.label}
                  </button>
                  {idx < navSteps.length - 1 && (
                    <span className="text-slate-300 text-xs">/</span>
                  )}
                </React.Fragment>
              );
            })}
          </nav>

          {/* Right: Cart Button & Quick Info */}
          <div className="flex items-center space-x-3">
            <button
              type="button"
              id="view-cart-nav-button"
              onClick={() => setView('cart')}
              className={`relative flex items-center space-x-2.5 px-3.5 py-2 rounded-xl border font-semibold text-xs transition-smooth ${
                view === 'cart'
                  ? 'bg-cyan-50 border-cyan-300 text-cyan-900'
                  : 'bg-white hover:bg-slate-50 border-slate-200 text-slate-800 hover:border-slate-300'
              }`}
            >
              <div className="relative">
                <ShoppingBag className="w-5 h-5 text-slate-700" />
                {totalCartCount > 0 && (
                  <span
                    id="cart-quantity-badge"
                    className="absolute -top-1.5 -right-2 bg-cyan-600 text-white font-bold text-[10px] w-4.5 h-4.5 rounded-full flex items-center justify-center animate-scale-in"
                  >
                    {totalCartCount}
                  </span>
                )}
              </div>
              <span className="hidden sm:inline">
                {totalCartCount > 0 ? `₹${cartSubtotal.toLocaleString()}` : 'Cart'}
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
