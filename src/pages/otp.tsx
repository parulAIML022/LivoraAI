import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, dashboardPathForRole } from "@/contexts/AuthContext";

export default function Otp() {
  const [otp, setOtp] = useState<string[]>(["", "", "", "", "", ""]);
  const inputsRef = useRef<Array<HTMLInputElement | null>>([]);
  const navigate = useNavigate();
  const { session, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && session) {
      navigate(dashboardPathForRole(session.role), { replace: true });
    }
  }, [session, isLoading, navigate]);

  const handleChange = (value: string, index: number) => {
    if (/^\d?$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);
      if (value && index < 5) {
        inputsRef.current[index + 1]?.focus();
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputsRef.current[index - 1]?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    navigate("/signin");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white shadow-md rounded-lg p-8 w-[400px] text-center">
        <h2 className="text-2xl font-bold text-green-600 mb-4">Verify OTP</h2>
        <p className="text-gray-600 mb-6">
          Email verification will be enabled in a later phase. Continue to sign in
          with your account.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="flex justify-between mb-6">
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(el) => (inputsRef.current[index] = el)}
                type="text"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(e.target.value, index)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                className="w-12 h-12 text-center text-lg font-bold border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
              />
            ))}
          </div>

          <button
            type="submit"
            className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700"
          >
            Continue to Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
