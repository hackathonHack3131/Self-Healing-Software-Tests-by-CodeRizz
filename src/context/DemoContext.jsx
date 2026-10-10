import React, { createContext, useContext, useState, useEffect } from 'react';
import { DEMO_PRODUCT } from '../data/product';

const DemoContext = createContext(null);

const STORAGE_KEY_CART = 'healtest_cart';
const STORAGE_KEY_VERSION = 'healtest_version';
const STORAGE_KEY_PRESET = 'healtest_preset';

export const DemoProvider = ({ children }) => {
  // Navigation view: 'product' | 'cart' | 'checkout' | 'confirmation'
  const [view, setView] = useState('product');

  // URL Version detection on initial mount
  const getInitialVersionAndPreset = () => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const urlVersion = params.get('version')?.toUpperCase();
      if (urlVersion === 'B') {
        return { version: 'B', preset: 'combined' };
      }
      if (urlVersion === 'A') {
        return { version: 'A', preset: 'baseline' };
      }
      const savedPreset = sessionStorage.getItem(STORAGE_KEY_PRESET);
      const savedVersion = sessionStorage.getItem(STORAGE_KEY_VERSION);
      if (savedPreset) {
        return {
          version: savedVersion || (savedPreset === 'baseline' ? 'A' : 'B'),
          preset: savedPreset
        };
      }
    }
    return { version: 'A', preset: 'baseline' };
  };

  const initialConfig = getInitialVersionAndPreset();
  const [version, setVersionState] = useState(initialConfig.version);
  const [preset, setPresetState] = useState(initialConfig.preset);

  // Cart state stored in sessionStorage
  const [cartItems, setCartItems] = useState(() => {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY_CART);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Simulated Payment Failure toggle
  const [simulatePaymentFailure, setSimulatePaymentFailure] = useState(false);

  // Processing state & error
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);
  const [paymentError, setPaymentError] = useState(null);

  // Last successful order details
  const [currentOrder, setCurrentOrder] = useState(null);

  // Toast feedback
  const [toastMessage, setToastMessage] = useState(null);

  // Checkout form details
  const initialForm = {
    fullName: '',
    email: '',
    address: '',
    postalCode: '',
    cardName: '',
    cardNumber: '',
    expiry: '',
    cvv: ''
  };
  const [checkoutForm, setCheckoutForm] = useState(initialForm);
  const [formErrors, setFormErrors] = useState({});

  // Sync cart to sessionStorage
  useEffect(() => {
    try {
      sessionStorage.setItem(STORAGE_KEY_CART, JSON.stringify(cartItems));
    } catch (e) {
      console.error('Failed to save cart to storage:', e);
    }
  }, [cartItems]);

  // Sync version to URL query param without full page reload
  const syncUrlParam = (newVersion) => {
    try {
      const url = new URL(window.location.href);
      url.searchParams.set('version', newVersion);
      window.history.replaceState({}, '', url.toString());
    } catch (e) {
      console.error('Failed to sync URL parameter:', e);
    }
  };

  // Change version
  const setVersion = (v) => {
    const norm = v.toUpperCase() === 'B' ? 'B' : 'A';
    setVersionState(norm);
    sessionStorage.setItem(STORAGE_KEY_VERSION, norm);
    syncUrlParam(norm);

    if (norm === 'A') {
      setPresetState('baseline');
      sessionStorage.setItem(STORAGE_KEY_PRESET, 'baseline');
    } else {
      setPresetState('combined');
      sessionStorage.setItem(STORAGE_KEY_PRESET, 'combined');
    }
  };

  // Change preset directly
  const setPreset = (p) => {
    setPresetState(p);
    sessionStorage.setItem(STORAGE_KEY_PRESET, p);
    if (p === 'baseline') {
      setVersionState('A');
      sessionStorage.setItem(STORAGE_KEY_VERSION, 'A');
      syncUrlParam('A');
    } else if (p === 'combined') {
      setVersionState('B');
      sessionStorage.setItem(STORAGE_KEY_VERSION, 'B');
      syncUrlParam('B');
    }
  };

  // Listen for browser popstate or manual URL changes
  useEffect(() => {
    const handleUrlCheck = () => {
      const params = new URLSearchParams(window.location.search);
      const urlVersion = params.get('version')?.toUpperCase();
      if (urlVersion === 'B' && version !== 'B') {
        setVersion('B');
      } else if (urlVersion === 'A' && version !== 'A') {
        setVersion('A');
      }
    };
    window.addEventListener('popstate', handleUrlCheck);
    return () => window.removeEventListener('popstate', handleUrlCheck);
  }, [version]);

  // Derived selector flags based on preset
  // Presets:
  // - Baseline: Version A with original selectors and layout.
  // - Renamed Elements: Change IDs and button labels. (Layout unchanged)
  // - Layout Changed: Move buttons and rearrange the form. (Selectors unchanged)
  // - Combined Redesign: Apply all Version B changes (renamed + layout changed).
  const isRenamedSelectors = preset === 'renamed' || preset === 'combined';
  const isRearrangedLayout = preset === 'layout' || preset === 'combined';

  // Dynamic Button Identifiers and Labels
  const checkoutButtonId = isRenamedSelectors ? 'proceed-to-payment' : 'checkout-button';
  const checkoutButtonLabel = isRenamedSelectors ? 'Continue to Payment' : 'Proceed to Checkout';

  const placeOrderButtonId = isRenamedSelectors ? 'confirm-purchase' : 'place-order';
  const placeOrderButtonLabel = isRenamedSelectors ? 'Confirm Purchase' : 'Place Order';

  // Toast helper
  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage((current) => (current === msg ? null : current));
    }, 3200);
  };

  // Cart operations
  const addToCart = (product = DEMO_PRODUCT, size = 'UK 9', quantity = 1) => {
    setCartItems((prev) => {
      const existingIndex = prev.findIndex(
        (item) => item.id === product.id && item.size === size
      );
      if (existingIndex > -1) {
        const next = [...prev];
        next[existingIndex] = {
          ...next[existingIndex],
          quantity: next[existingIndex].quantity + quantity
        };
        return next;
      }
      return [
        ...prev,
        {
          id: product.id,
          name: product.name,
          price: product.price,
          image: product.image,
          size,
          quantity
        }
      ];
    });
    showToast(`Added ${product.name} (${size}) to cart!`);
  };

  const updateQuantity = (id, size, newQty) => {
    if (newQty <= 0) {
      removeFromCart(id, size);
      return;
    }
    setCartItems((prev) =>
      prev.map((item) =>
        item.id === id && item.size === size ? { ...item, quantity: newQty } : item
      )
    );
  };

  const removeFromCart = (id, size) => {
    setCartItems((prev) => prev.filter((item) => !(item.id === id && item.size === size)));
    showToast('Item removed from cart.');
  };

  const clearCart = () => {
    setCartItems([]);
  };

  const totalCartCount = cartItems.reduce((acc, item) => acc + item.quantity, 0);
  const cartSubtotal = cartItems.reduce((acc, item) => acc + item.price * item.quantity, 0);

  // Form updates
  const updateFormField = (field, value) => {
    setCheckoutForm((prev) => ({ ...prev, [field]: value }));
    if (formErrors[field]) {
      setFormErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  // Quick fill dummy values for test execution
  const quickFillDummy = () => {
    setCheckoutForm({
      fullName: 'John Doe',
      email: 'john.doe@example.com',
      address: '42 Falcon Ridge Boulevard, Suite 300',
      postalCode: '560001',
      cardName: 'John Doe',
      cardNumber: '4242 4242 4242 4242',
      expiry: '12/30',
      cvv: '123'
    });
    setFormErrors({});
    showToast('Filled dummy checkout credentials.');
  };

  // Validate form
  const validateForm = () => {
    const errors = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!checkoutForm.fullName.trim()) {
      errors.fullName = 'Full name is required';
    }
    if (!checkoutForm.email.trim()) {
      errors.email = 'Email address is required';
    } else if (!emailRegex.test(checkoutForm.email.trim())) {
      errors.email = 'Please provide a valid email address';
    }
    if (!checkoutForm.address.trim()) {
      errors.address = 'Shipping address is required';
    }
    if (!checkoutForm.postalCode.trim()) {
      errors.postalCode = 'Postal code is required';
    } else if (checkoutForm.postalCode.trim().length < 4) {
      errors.postalCode = 'Invalid postal code format';
    }

    if (!checkoutForm.cardName.trim()) {
      errors.cardName = 'Cardholder name is required';
    }
    const cleanCard = checkoutForm.cardNumber.replace(/\s+/g, '');
    if (!cleanCard) {
      errors.cardNumber = 'Card number is required';
    } else if (cleanCard.length < 15 || cleanCard.length > 19) {
      errors.cardNumber = 'Card number must be 16 digits (e.g. 4242 4242 4242 4242)';
    }

    if (!checkoutForm.expiry.trim()) {
      errors.expiry = 'Expiry date required';
    } else if (!/^\d{2}\/\d{2}$/.test(checkoutForm.expiry.trim())) {
      errors.expiry = 'Use MM/YY format (e.g. 12/30)';
    }

    if (!checkoutForm.cvv.trim()) {
      errors.cvv = 'CVV required';
    } else if (!/^\d{3,4}$/.test(checkoutForm.cvv.trim())) {
      errors.cvv = 'CVV must be 3 or 4 digits';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Process checkout submission
  const submitCheckout = () => {
    if (isProcessingPayment) return;

    setPaymentError(null);
    const isValid = validateForm();
    if (!isValid) {
      return { success: false, reason: 'validation_failed' };
    }

    if (cartItems.length === 0) {
      setPaymentError('Your cart is empty. Please add items before checking out.');
      return { success: false, reason: 'empty_cart' };
    }

    setIsProcessingPayment(true);

    // Simulate network delay for realistic test interaction
    setTimeout(() => {
      setIsProcessingPayment(false);

      if (simulatePaymentFailure) {
        setPaymentError('Payment Declined — Please try again.');
        // Do not create an order or show confirmation
        return;
      }

      // Success branch
      const randomOrderNumber = Math.floor(100000 + Math.random() * 900000);
      const newOrder = {
        orderId: `ORD-HT-${randomOrderNumber}`,
        date: new Date().toLocaleDateString('en-IN', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        }),
        items: [...cartItems],
        totalAmount: cartSubtotal,
        customer: { ...checkoutForm },
        last4: checkoutForm.cardNumber.replace(/\s+/g, '').slice(-4) || '4242',
        isSimulated: true
      };

      setCurrentOrder(newOrder);
      setCartItems([]);
      setView('confirmation');
      setPaymentError(null);
    }, 600);
  };

  // Reset Demo State (Feature 3)
  const resetDemoState = () => {
    setCartItems([]);
    setCheckoutForm(initialForm);
    setFormErrors({});
    setCurrentOrder(null);
    setPaymentError(null);
    setIsProcessingPayment(false);
    setView('product');
    showToast('Demo state reset: Cart, checkout & orders cleared.');
  };

  return (
    <DemoContext.Provider
      value={{
        view,
        setView,
        version,
        setVersion,
        preset,
        setPreset,
        isRenamedSelectors,
        isRearrangedLayout,
        checkoutButtonId,
        checkoutButtonLabel,
        placeOrderButtonId,
        placeOrderButtonLabel,
        cartItems,
        totalCartCount,
        cartSubtotal,
        addToCart,
        updateQuantity,
        removeFromCart,
        clearCart,
        checkoutForm,
        updateFormField,
        quickFillDummy,
        formErrors,
        simulatePaymentFailure,
        setSimulatePaymentFailure,
        isProcessingPayment,
        paymentError,
        setPaymentError,
        currentOrder,
        submitCheckout,
        resetDemoState,
        toastMessage
      }}
    >
      {children}
    </DemoContext.Provider>
  );
};

export const useDemo = () => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemo must be used within a DemoProvider');
  }
  return context;
};
