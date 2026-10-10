import React from 'react';
import { useDemo } from '../context/DemoContext';
import {
  CheckCircle2,
  ArrowRight,
  Package,
  Calendar,
  CreditCard,
  MapPin,
  ShieldCheck,
  RotateCcw,
  Sparkles
} from 'lucide-react';

export const OrderConfirmationPage = () => {
  const { currentOrder, setView, resetDemoState } = useDemo();

  if (!currentOrder) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm space-y-4">
          <Package className="w-12 h-12 text-slate-400 mx-auto" />
          <h2 className="text-xl font-bold text-slate-800">No Active Order Found</h2>
          <p className="text-xs text-slate-500">
            It looks like no checkout has been completed yet.
          </p>
          <button
            type="button"
            onClick={() => setView('product')}
            className="px-6 py-2.5 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800 transition-smooth"
          >
            Go to Product Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10 sm:py-16">
      <div className="bg-white rounded-3xl border border-slate-200/90 shadow-xl overflow-hidden">
        {/* Success Header Banner */}
        <div className="bg-gradient-to-br from-slate-900 via-slate-950 to-indigo-950 text-white p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 translate-x-8 -translate-y-8 w-40 h-40 bg-cyan-500/10 rounded-full blur-2xl"></div>

          <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center mx-auto mb-4 animate-scale-in">
            <CheckCircle2 className="w-10 h-10 text-emerald-400" />
          </div>

          <span className="text-[11px] font-mono uppercase tracking-widest text-cyan-300 font-bold bg-cyan-950/60 border border-cyan-800/80 px-3 py-1 rounded-full">
            Simulated Purchase Successful
          </span>

          <h1 id="order-success-title" className="text-2xl sm:text-3xl font-black mt-3 tracking-tight">
            Order Successful!
          </h1>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-md mx-auto">
            Thank you for participating in the HealTest AI automated self-healing test run.
          </p>

          <div className="mt-5 inline-flex items-center space-x-2 bg-slate-800/80 border border-slate-700/80 px-4 py-2 rounded-xl text-xs font-mono">
            <span className="text-slate-400">Order ID:</span>
            <span id="order-id-display" className="text-cyan-300 font-bold tracking-wider">
              {currentOrder.orderId}
            </span>
          </div>
        </div>

        {/* Notice of Simulation */}
        <div className="bg-amber-50 border-y border-amber-200/80 px-6 py-3 text-xs text-amber-900 flex items-center space-x-2.5">
          <ShieldCheck className="w-4 h-4 text-amber-600 shrink-0" />
          <p>
            <strong>Simulated Testing Environment:</strong> No real payment was charged, and no physical items will be shipped.
          </p>
        </div>

        {/* Order Details Body */}
        <div className="p-6 sm:p-8 space-y-6">
          {/* Metadata Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pb-6 border-b border-slate-100 text-xs">
            <div className="space-y-1">
              <span className="text-slate-400 uppercase tracking-wider font-semibold text-[10px]">Date</span>
              <p className="font-semibold text-slate-800 flex items-center space-x-1">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                <span>{currentOrder.date}</span>
              </p>
            </div>
            <div className="space-y-1">
              <span className="text-slate-400 uppercase tracking-wider font-semibold text-[10px]">Payment Method</span>
              <p className="font-semibold text-slate-800 flex items-center space-x-1">
                <CreditCard className="w-3.5 h-3.5 text-slate-400" />
                <span>Visa •••• {currentOrder.last4}</span>
              </p>
            </div>
            <div className="space-y-1">
              <span className="text-slate-400 uppercase tracking-wider font-semibold text-[10px]">Recipient</span>
              <p className="font-semibold text-slate-800 truncate">
                {currentOrder.customer.fullName}
              </p>
            </div>
          </div>

          {/* Purchased Items List */}
          <div>
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3">
              Purchased Product(s)
            </h2>
            <div className="space-y-3">
              {currentOrder.items.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80"
                >
                  <div className="flex items-center space-x-3.5">
                    <div className="w-14 h-14 rounded-xl bg-white p-1 border border-slate-200 shrink-0 overflow-hidden">
                      <img src={item.image} alt={item.name} className="w-full h-full object-contain" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm text-slate-900">{item.name}</h3>
                      <p className="text-xs text-slate-500">
                        Size: <span className="font-semibold text-slate-700">{item.size}</span> | Qty:{' '}
                        <span className="font-semibold text-slate-700">{item.quantity}</span>
                      </p>
                    </div>
                  </div>
                  <span className="font-mono font-bold text-sm text-slate-900">
                    ₹{(item.price * item.quantity).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Price Calculation */}
          <div className="bg-slate-50 rounded-2xl p-4 border border-slate-200/80 space-y-2 text-xs">
            <div className="flex justify-between text-slate-600">
              <span>Subtotal</span>
              <span className="font-mono font-semibold">₹{currentOrder.totalAmount.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>Express Delivery</span>
              <span className="text-emerald-600 font-bold uppercase">FREE</span>
            </div>
            <div className="pt-2 border-t border-slate-200 flex justify-between items-baseline">
              <span className="text-sm font-bold text-slate-900">Total Paid (Simulated)</span>
              <span id="order-total-amount" className="text-xl font-black text-slate-950 font-mono">
                ₹{currentOrder.totalAmount.toLocaleString()}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <button
              type="button"
              id="continue-shopping-order-btn"
              onClick={() => setView('product')}
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl font-bold text-xs bg-slate-900 hover:bg-slate-800 text-white transition-smooth flex items-center justify-center space-x-2"
            >
              <span>Continue Shopping</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              id="reset-from-confirmation-btn"
              onClick={resetDemoState}
              className="w-full sm:w-auto px-5 py-3.5 rounded-xl font-semibold text-xs text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-100 border border-slate-200 transition-smooth flex items-center justify-center space-x-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Demo State</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
