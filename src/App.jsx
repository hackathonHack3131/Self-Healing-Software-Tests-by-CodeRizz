import React from 'react';
import { DemoProvider, useDemo } from './context/DemoContext';
import { DevControls } from './components/DevControls';
import { Navbar } from './components/Navbar';
import { ProductPage } from './components/ProductPage';
import { CartPage } from './components/CartPage';
import { CheckoutPage } from './components/CheckoutPage';
import { OrderConfirmationPage } from './components/OrderConfirmationPage';
import { ShieldAlert, CheckCircle2, Terminal } from 'lucide-react';

function AppContent() {
  const { view, toastMessage, version, preset } = useDemo();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      {/* Developer Control Toolbar (Feature 1, 2, 3 + Version A/B Switcher) */}
      <DevControls />

      {/* Main E-Commerce Navigation Bar */}
      <Navbar />

      {/* Main Application Content Container */}
      <main className="flex-1">
        {view === 'product' && <ProductPage />}
        {view === 'cart' && <CartPage />}
        {view === 'checkout' && <CheckoutPage />}
        {view === 'confirmation' && <OrderConfirmationPage />}
      </main>

      {/* Floating Feedback Toast */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-4 py-3 rounded-2xl shadow-2xl border border-slate-700 text-xs font-semibold flex items-center space-x-2.5 animate-slide-up">
          <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Demonstration Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12 py-8 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span className="font-semibold text-slate-700">HealTest AI Target Application</span>
            <span>•</span>
            <span className="font-mono text-slate-400">Phase 1 Demo Environment</span>
          </div>
          <div className="flex items-center space-x-4 text-slate-400 font-mono text-[11px]">
            <span>Active Version: <strong className="text-slate-700">{version}</strong></span>
            <span>Preset: <strong className="text-slate-700">{preset}</strong></span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <DemoProvider>
      <AppContent />
    </DemoProvider>
  );
}
