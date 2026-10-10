import React from 'react';
import { useDemo } from '../context/DemoContext';
import {
  CreditCard,
  Lock,
  ArrowLeft,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Loader2,
  Sparkles,
  ShieldCheck,
  ShoppingBag
} from 'lucide-react';

export const CheckoutPage = () => {
  const {
    cartItems,
    cartSubtotal,
    checkoutForm,
    updateFormField,
    quickFillDummy,
    formErrors,
    submitCheckout,
    isProcessingPayment,
    paymentError,
    setView,
    placeOrderButtonId,
    placeOrderButtonLabel,
    isRearrangedLayout
  } = useDemo();

  const handleSubmit = (e) => {
    e.preventDefault();
    submitCheckout();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      {/* Header & Back Action */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <button
            type="button"
            id="back-to-cart-btn"
            onClick={() => setView('cart')}
            className="text-xs font-semibold text-slate-500 hover:text-slate-800 flex items-center space-x-1.5 mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Cart</span>
          </button>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-950 tracking-tight">
            Checkout & Simulated Payment
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Complete the form with simulated test credentials to complete the order.
          </p>
        </div>

        {/* Quick Autofill Helper for Automated & Manual Testing */}
        <div className="flex items-center space-x-2">
          <button
            type="button"
            id="quick-fill-btn"
            onClick={quickFillDummy}
            className="px-3.5 py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 rounded-xl text-xs font-semibold transition-smooth flex items-center space-x-1.5 shadow-2xs"
            title="Auto-fill with valid test card credentials"
          >
            <Sparkles className="w-4 h-4 text-indigo-600" />
            <span>⚡ Fill Dummy Credentials</span>
          </button>
        </div>
      </div>

      {/* Simulated Payment Error Banner (Feature 2) */}
      {paymentError && (
        <div
          id="payment-error-alert"
          role="alert"
          className="mb-8 p-4 rounded-2xl bg-rose-50 border-2 border-rose-300 text-rose-900 flex items-start space-x-3.5 shadow-md animate-scale-in"
        >
          <AlertCircle className="w-6 h-6 text-rose-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="font-bold text-sm text-rose-950">Transaction Failed</h3>
            <p className="text-xs text-rose-800 font-medium">
              {paymentError}
            </p>
            <p className="text-[11px] text-rose-600">
              Note: This failure is triggered by the developer simulator toggle. Disable the toggle in the top bar to proceed.
            </p>
          </div>
        </div>
      )}

      {/* Main Checkout Grid: Version A vs Version B Layout */}
      <form onSubmit={handleSubmit} noValidate>
        {isRearrangedLayout ? (
          /* ==========================================================
             VERSION B REARRANGED LAYOUT:
             Reordered form with Side-by-Side sections and Order Summary
             hosting the Primary Purchase Button
             ========================================================== */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start" data-layout="redesigned-b">
            {/* Left 7 Columns: Form with alternative card styling */}
            <div className="lg:col-span-7 space-y-6">
              {/* Customer Details Section */}
              <div className="bg-white rounded-3xl p-6 sm:p-7 border-2 border-slate-200/90 shadow-sm space-y-5">
                <div className="flex items-center space-x-2 pb-3 border-b border-slate-100">
                  <span className="w-6 h-6 rounded-full bg-indigo-600 text-white font-mono text-xs font-bold flex items-center justify-center">
                    1
                  </span>
                  <h2 className="text-base font-bold text-slate-900">
                    Recipient & Delivery Address
                  </h2>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="full-name-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Full Name *
                    </label>
                    <input
                      id="full-name-input"
                      name="fullName"
                      type="text"
                      placeholder="e.g. John Doe"
                      value={checkoutForm.fullName}
                      onChange={(e) => updateFormField('fullName', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.fullName
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100'
                      }`}
                    />
                    {formErrors.fullName && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.fullName}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="email-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Email Address *
                    </label>
                    <input
                      id="email-input"
                      name="email"
                      type="email"
                      placeholder="e.g. john.doe@example.com"
                      value={checkoutForm.email}
                      onChange={(e) => updateFormField('email', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.email
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100'
                      }`}
                    />
                    {formErrors.email && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.email}</p>
                    )}
                  </div>

                  <div className="sm:col-span-2">
                    <label htmlFor="address-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Street / Shipping Address *
                    </label>
                    <input
                      id="address-input"
                      name="address"
                      type="text"
                      placeholder="Flat, Building, Street, Area"
                      value={checkoutForm.address}
                      onChange={(e) => updateFormField('address', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.address
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100'
                      }`}
                    />
                    {formErrors.address && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.address}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="postal-code-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Postal Code / PIN *
                    </label>
                    <input
                      id="postal-code-input"
                      name="postalCode"
                      type="text"
                      placeholder="e.g. 560001"
                      value={checkoutForm.postalCode}
                      onChange={(e) => updateFormField('postalCode', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.postalCode
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100'
                      }`}
                    />
                    {formErrors.postalCode && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.postalCode}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Simulated Payment Section */}
              <div className="bg-white rounded-3xl p-6 sm:p-7 border-2 border-indigo-100 shadow-md space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-full bg-indigo-600 text-white font-mono text-xs font-bold flex items-center justify-center">
                      2
                    </span>
                    <h2 className="text-base font-bold text-slate-900">
                      Simulated Payment (vB Card Layout)
                    </h2>
                  </div>
                  <span className="text-[11px] font-mono bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded font-semibold">
                    Simulated Sandbox
                  </span>
                </div>

                {/* Dummy Value Guidance Box */}
                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600 space-y-1">
                  <div className="font-semibold text-slate-800 flex items-center space-x-1.5">
                    <Lock className="w-3.5 h-3.5 text-indigo-600" />
                    <span>Dummy test values allowed:</span>
                  </div>
                  <div className="font-mono text-[11px] text-slate-700 grid grid-cols-3 gap-1">
                    <span>Card: 4242 4242 4242 4242</span>
                    <span>Exp: 12/30</span>
                    <span>CVV: 123</span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label htmlFor="card-name-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Cardholder Name *
                    </label>
                    <input
                      id="card-name-input"
                      name="cardName"
                      type="text"
                      placeholder="Name on card"
                      value={checkoutForm.cardName}
                      onChange={(e) => updateFormField('cardName', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.cardName
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100'
                      }`}
                    />
                    {formErrors.cardName && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.cardName}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="card-number-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Simulated Card Number *
                    </label>
                    <div className="relative">
                      <input
                        id="card-number-input"
                        name="cardNumber"
                        type="text"
                        placeholder="4242 4242 4242 4242"
                        value={checkoutForm.cardNumber}
                        onChange={(e) => updateFormField('cardNumber', e.target.value)}
                        className={`w-full pl-10 pr-3.5 py-2.5 rounded-xl border font-mono text-sm transition-smooth ${
                          formErrors.cardNumber
                            ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                            : 'border-slate-300 bg-white focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100'
                        }`}
                      />
                      <CreditCard className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                    </div>
                    {formErrors.cardNumber && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.cardNumber}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="expiry-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                        Expiry Date *
                      </label>
                      <input
                        id="expiry-input"
                        name="expiry"
                        type="text"
                        placeholder="MM/YY (12/30)"
                        value={checkoutForm.expiry}
                        onChange={(e) => updateFormField('expiry', e.target.value)}
                        className={`w-full px-3.5 py-2.5 rounded-xl border font-mono text-sm transition-smooth ${
                          formErrors.expiry
                            ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                            : 'border-slate-300 bg-white focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100'
                        }`}
                      />
                      {formErrors.expiry && (
                        <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.expiry}</p>
                      )}
                    </div>

                    <div>
                      <label htmlFor="cvv-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                        Security Code / CVV *
                      </label>
                      <input
                        id="cvv-input"
                        name="cvv"
                        type="password"
                        maxLength={4}
                        placeholder="123"
                        value={checkoutForm.cvv}
                        onChange={(e) => updateFormField('cvv', e.target.value)}
                        className={`w-full px-3.5 py-2.5 rounded-xl border font-mono text-sm transition-smooth ${
                          formErrors.cvv
                            ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                            : 'border-slate-300 bg-white focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100'
                        }`}
                      />
                      {formErrors.cvv && (
                        <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.cvv}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right 5 Columns: Summary Hosting the Version B Button */}
            <div className="lg:col-span-5 space-y-4">
              <div className="bg-slate-900 rounded-3xl p-6 text-white shadow-xl space-y-5 border border-slate-800">
                <div className="flex items-center justify-between pb-4 border-b border-slate-800">
                  <h2 className="text-base font-bold text-white flex items-center space-x-2">
                    <ShoppingBag className="w-4 h-4 text-cyan-400" />
                    <span>Purchase Summary</span>
                  </h2>
                  <span className="text-xs text-slate-400 font-mono">vB Relocated Submit</span>
                </div>

                {/* Items preview */}
                <div className="space-y-3 max-h-48 overflow-y-auto pr-1">
                  {cartItems.map((item) => (
                    <div key={`${item.id}-${item.size}`} className="flex items-center justify-between text-xs py-1">
                      <div className="flex items-center space-x-2.5">
                        <img src={item.image} alt={item.name} className="w-8 h-8 rounded-lg bg-slate-800 p-0.5 object-contain" />
                        <div>
                          <p className="font-semibold text-slate-200 line-clamp-1">{item.name}</p>
                          <p className="text-[10px] text-slate-400">Qty: {item.quantity} | Size: {item.size}</p>
                        </div>
                      </div>
                      <span className="font-mono font-bold text-slate-200">₹{(item.price * item.quantity).toLocaleString()}</span>
                    </div>
                  ))}
                </div>

                <div className="border-t border-slate-800 pt-3 space-y-2 text-xs text-slate-300">
                  <div className="flex justify-between">
                    <span>Subtotal</span>
                    <span className="font-mono">₹{cartSubtotal.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Delivery</span>
                    <span className="text-cyan-400 font-bold uppercase">FREE</span>
                  </div>
                  <div className="pt-2 border-t border-slate-800 flex justify-between items-baseline">
                    <span className="text-sm font-bold text-white">Amount Due</span>
                    <span className="text-2xl font-black text-cyan-400 font-mono">₹{cartSubtotal.toLocaleString()}</span>
                  </div>
                </div>

                {/* VERSION B FINAL SUBMIT BUTTON: Repositioned inside the order summary */}
                <button
                  type="submit"
                  id={placeOrderButtonId}
                  disabled={isProcessingPayment}
                  className="w-full py-4 rounded-2xl font-extrabold text-sm bg-gradient-to-r from-cyan-400 to-indigo-400 hover:from-cyan-300 hover:to-indigo-300 text-slate-950 shadow-lg shadow-cyan-500/25 transition-all active:scale-98 flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {isProcessingPayment ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Processing Payment...</span>
                    </>
                  ) : (
                    <>
                      <Lock className="w-4 h-4 text-slate-950" />
                      <span>{placeOrderButtonLabel} — ₹{cartSubtotal.toLocaleString()}</span>
                    </>
                  )}
                </button>
              </div>

              <div className="bg-white rounded-2xl p-4 border border-slate-200/80 text-xs text-slate-500 flex items-center space-x-2.5">
                <ShieldCheck className="w-4 h-4 text-indigo-600 shrink-0" />
                <span>Playwright test runner target: Identifier #{placeOrderButtonId}</span>
              </div>
            </div>
          </div>
        ) : (
          /* ==========================================================
             VERSION A BASELINE LAYOUT:
             Predictable layout: Left customer & payment form with
             Place Order button placed directly below the payment fields.
             ========================================================== */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start" data-layout="baseline-a">
            {/* Left 8 Columns: Form with baseline button location */}
            <div className="lg:col-span-8 space-y-6">
              {/* Customer details card */}
              <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-sm space-y-5">
                <h2 className="text-base font-bold text-slate-900 pb-3 border-b border-slate-100">
                  Customer & Shipping Information
                </h2>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="full-name-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Full Name *
                    </label>
                    <input
                      id="full-name-input"
                      name="fullName"
                      type="text"
                      placeholder="e.g. John Doe"
                      value={checkoutForm.fullName}
                      onChange={(e) => updateFormField('fullName', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.fullName
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100'
                      }`}
                    />
                    {formErrors.fullName && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.fullName}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="email-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Email Address *
                    </label>
                    <input
                      id="email-input"
                      name="email"
                      type="email"
                      placeholder="e.g. john.doe@example.com"
                      value={checkoutForm.email}
                      onChange={(e) => updateFormField('email', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.email
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100'
                      }`}
                    />
                    {formErrors.email && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.email}</p>
                    )}
                  </div>

                  <div className="sm:col-span-2">
                    <label htmlFor="address-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Shipping Address *
                    </label>
                    <input
                      id="address-input"
                      name="address"
                      type="text"
                      placeholder="Flat, Building, Street, Area"
                      value={checkoutForm.address}
                      onChange={(e) => updateFormField('address', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.address
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100'
                      }`}
                    />
                    {formErrors.address && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.address}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="postal-code-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Postal Code *
                    </label>
                    <input
                      id="postal-code-input"
                      name="postalCode"
                      type="text"
                      placeholder="e.g. 560001"
                      value={checkoutForm.postalCode}
                      onChange={(e) => updateFormField('postalCode', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.postalCode
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100'
                      }`}
                    />
                    {formErrors.postalCode && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.postalCode}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Payment Details Card */}
              <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/90 shadow-sm space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <h2 className="text-base font-bold text-slate-900">
                    Simulated Card Payment
                  </h2>
                  <div className="flex items-center space-x-1.5 text-xs text-slate-500 font-mono">
                    <Lock className="w-3.5 h-3.5 text-slate-400" />
                    <span>Demo Mode</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600">
                  <p className="font-semibold text-slate-800">Use dummy values:</p>
                  <p className="font-mono text-[11px] text-slate-600 mt-0.5">
                    Card: 4242 4242 4242 4242 &nbsp;|&nbsp; Exp: 12/30 &nbsp;|&nbsp; CVV: 123
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label htmlFor="card-name-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Cardholder Name *
                    </label>
                    <input
                      id="card-name-input"
                      name="cardName"
                      type="text"
                      placeholder="e.g. John Doe"
                      value={checkoutForm.cardName}
                      onChange={(e) => updateFormField('cardName', e.target.value)}
                      className={`w-full px-3.5 py-2.5 rounded-xl border text-sm transition-smooth ${
                        formErrors.cardName
                          ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                          : 'border-slate-300 bg-white focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100'
                      }`}
                    />
                    {formErrors.cardName && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.cardName}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="card-number-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                      Card Number *
                    </label>
                    <div className="relative">
                      <input
                        id="card-number-input"
                        name="cardNumber"
                        type="text"
                        placeholder="4242 4242 4242 4242"
                        value={checkoutForm.cardNumber}
                        onChange={(e) => updateFormField('cardNumber', e.target.value)}
                        className={`w-full pl-10 pr-3.5 py-2.5 rounded-xl border font-mono text-sm transition-smooth ${
                          formErrors.cardNumber
                            ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                            : 'border-slate-300 bg-white focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100'
                        }`}
                      />
                      <CreditCard className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                    </div>
                    {formErrors.cardNumber && (
                      <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.cardNumber}</p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="expiry-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                        Expiry Date *
                      </label>
                      <input
                        id="expiry-input"
                        name="expiry"
                        type="text"
                        placeholder="12/30"
                        value={checkoutForm.expiry}
                        onChange={(e) => updateFormField('expiry', e.target.value)}
                        className={`w-full px-3.5 py-2.5 rounded-xl border font-mono text-sm transition-smooth ${
                          formErrors.expiry
                            ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                            : 'border-slate-300 bg-white focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100'
                        }`}
                      />
                      {formErrors.expiry && (
                        <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.expiry}</p>
                      )}
                    </div>

                    <div>
                      <label htmlFor="cvv-input" className="block text-xs font-bold text-slate-700 uppercase mb-1">
                        CVV *
                      </label>
                      <input
                        id="cvv-input"
                        name="cvv"
                        type="password"
                        maxLength={4}
                        placeholder="123"
                        value={checkoutForm.cvv}
                        onChange={(e) => updateFormField('cvv', e.target.value)}
                        className={`w-full px-3.5 py-2.5 rounded-xl border font-mono text-sm transition-smooth ${
                          formErrors.cvv
                            ? 'border-rose-400 bg-rose-50/50 text-rose-950 focus:ring-rose-200'
                            : 'border-slate-300 bg-white focus:border-cyan-600 focus:ring-2 focus:ring-cyan-100'
                        }`}
                      />
                      {formErrors.cvv && (
                        <p className="text-[11px] text-rose-600 mt-1 font-medium">{formErrors.cvv}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* VERSION A BASELINE FINAL SUBMISSION BUTTON (Placed directly inside payment card) */}
                <div className="pt-4 border-t border-slate-100">
                  <button
                    type="submit"
                    id={placeOrderButtonId}
                    disabled={isProcessingPayment}
                    className="w-full py-4 rounded-2xl font-bold text-sm bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20 transition-all active:scale-98 flex items-center justify-center space-x-2 disabled:opacity-50"
                  >
                    {isProcessingPayment ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin text-slate-950" />
                        <span>Processing Payment...</span>
                      </>
                    ) : (
                      <>
                        <Lock className="w-4 h-4 text-slate-950" />
                        <span>{placeOrderButtonLabel}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Right 4 Columns: Order Summary Card (Version A) */}
            <div className="lg:col-span-4 space-y-4">
              <div className="bg-white rounded-3xl p-6 border border-slate-200/90 shadow-sm space-y-4">
                <h2 className="text-base font-bold text-slate-900 pb-3 border-b border-slate-100">
                  Order Summary
                </h2>

                <div className="space-y-3">
                  {cartItems.map((item) => (
                    <div key={`${item.id}-${item.size}`} className="flex items-center justify-between text-xs py-1">
                      <div className="flex items-center space-x-2.5">
                        <img src={item.image} alt={item.name} className="w-10 h-10 rounded-lg bg-slate-100 p-1 object-contain" />
                        <div>
                          <p className="font-semibold text-slate-900 line-clamp-1">{item.name}</p>
                          <p className="text-[11px] text-slate-500">Qty: {item.quantity} | Size: {item.size}</p>
                        </div>
                      </div>
                      <span className="font-mono font-bold text-slate-900">₹{(item.price * item.quantity).toLocaleString()}</span>
                    </div>
                  ))}
                </div>

                <div className="pt-3 border-t border-slate-100 space-y-2 text-xs">
                  <div className="flex justify-between text-slate-600">
                    <span>Subtotal</span>
                    <span className="font-semibold text-slate-900">₹{cartSubtotal.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>Shipping</span>
                    <span className="text-emerald-600 font-semibold uppercase">Free</span>
                  </div>
                  <div className="pt-2 border-t border-slate-100 flex justify-between items-baseline">
                    <span className="text-sm font-bold text-slate-900">Total Price</span>
                    <span className="text-xl font-black text-slate-950 font-mono">₹{cartSubtotal.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-4 border border-slate-200/80 text-xs text-slate-500 flex items-center space-x-2.5">
                <ShieldCheck className="w-4 h-4 text-cyan-600 shrink-0" />
                <span>Playwright test runner target: Identifier #{placeOrderButtonId}</span>
              </div>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};
