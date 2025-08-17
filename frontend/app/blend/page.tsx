"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Film, ArrowRight, User, LinkIcon } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { toast } from "sonner"

export default function BlendPage() {
  const [profile1, setProfile1] = useState("")
  const [profile2, setProfile2] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<{ profile1?: string, profile2?: string }>({})
  const router = useRouter()

  // Allow any input for profile fields, only require both are filled and not identical
  const validateUrls = (): boolean => {
    const newErrors: { profile1?: string, profile2?: string } = {}

    if (!profile1) {
      newErrors.profile1 = "Please enter a profile."
    }
    if (!profile2) {
      newErrors.profile2 = "Please enter a profile."
    }
    if (profile1 && profile2 && profile1 === profile2) {
      newErrors.profile1 = "Please enter different profiles."
      newErrors.profile2 = "Please enter different profiles."
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleMockBlend = async () => {
    setIsLoading(true)

    try {
      const response = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + 'mock', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        const errorData = await response.json()

        if (response.status === 429) {
          toast.error("API Budget Exhausted", {
            description: "All API keys have been used. Please try again tomorrow.",
            duration: 5000,
          })
        } else {
          toast.error("Error", {
            description: errorData.detail || `Failed to get example data: ${response.statusText}`,
            duration: 4000,
          })
        }

        return
      }

      const recommendations = await response.json()
      localStorage.setItem('blendResults', JSON.stringify(recommendations))

      toast.success("Data Loaded!", {
        description: `Loaded ${recommendations.length} sample movie recommendations.`,
        duration: 3000,
      })

      router.push("/results")
    } catch (error) {
      console.error('Error getting example data:', error)
      toast.error("Network Error", {
        description: "Failed to connect to the server. Please try again.",
        duration: 4000,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const toLetterboxdFilmsUrl = (input: string) => {
    const s = input.trim();
    if (/^https?:\/\/letterboxd\.com\/[a-zA-Z0-9_-]+\/films\/?$/.test(s)) return s.endsWith('/') ? s : s + '/';
    const match = s.match(/^https?:\/\/letterboxd\.com\/([a-zA-Z0-9_-]+)\/?$/);
    if (match) return `https://letterboxd.com/${match[1]}/films/`;
    if (/^[a-zA-Z0-9_-]+$/.test(s)) return `https://letterboxd.com/${s}/films/`;
    return s;
  };

  const handleBlend = async () => {
    if (!validateUrls()) {
      return;
    }

    setIsLoading(true);

    const user1_url = toLetterboxdFilmsUrl(profile1);
    const user2_url = toLetterboxdFilmsUrl(profile2);

    try {
      const response = await fetch(process.env.NEXT_PUBLIC_BACKEND_URL + 'blend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user1_url,
          user2_url,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();

        if (response.status === 429) {
          toast.error("API Budget Exhausted", {
            description: "All API keys have been used. Please try again tomorrow.",
            duration: 5000,
          });
        } else {
          toast.error("Blend Failed", {
            description: errorData.detail || `Failed to blend profiles: ${response.statusText}`,
            duration: 4000,
          });
        }

        return;
      }

      const recommendations = await response.json();
      localStorage.setItem('blendResults', JSON.stringify(recommendations));

      toast.success("Blend Complete!", {
        description: `Found ${recommendations.length} perfect movie matches for you both.`,
        duration: 3000,
      });

      router.push("/results");
    } catch (error) {
      toast.error("Network Error", {
        description: "Failed to connect to the server. Please try again.",
        duration: 4000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-red-950 to-gray-900 overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-32 left-16 w-40 h-40 bg-red-500/20 rounded-full blur-2xl"
          animate={{
            x: [0, 80, 0],
            y: [0, -60, 0],
            scale: [1, 1.3, 1],
          }}
          transition={{
            duration: 12,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-32 right-20 w-32 h-32 bg-orange-500/20 rounded-full blur-2xl"
          animate={{
            x: [0, -60, 0],
            y: [0, 40, 0],
            scale: [1, 0.9, 1],
          }}
          transition={{
            duration: 8,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-16">
        {/* Header */}
        <motion.header
          className="flex items-center justify-between mb-16"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-r from-red-500 to-red-600 rounded-lg flex items-center justify-center">
              <Film className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">CinemaBlend</span>
          </Link>
        </motion.header>

        {/* Main Content */}
        <div className="max-w-2xl mx-auto">
          <motion.div
            className="text-center mb-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-red-400 via-orange-400 to-red-500 bg-clip-text text-transparent">
              Create Your Blend
            </h1>
            <p className="text-xl text-white/80 mb-8">
              Enter two Letterboxd profile usernames to discover your perfect movie matches
            </p>
          </motion.div>

          <motion.div
            className="bg-white/5 backdrop-blur-sm rounded-3xl p-8 border border-red-500/20 shadow-2xl"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="space-y-8">
              {/* Profile 1 */}
              <div className="space-y-3">
                <Label htmlFor="profile1" className="text-white font-medium flex items-center gap-2">
                  <div className="w-6 h-6 bg-gradient-to-r from-red-500 to-red-600 rounded-full flex items-center justify-center">
                    <User className="w-3 h-3 text-white" />
                  </div>
                  First Profile
                </Label>
                <div className="relative">
                  <LinkIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/50" />
                  <Input
                    id="profile1"
                    type="url"
                    placeholder="Username"
                    value={profile1}
                    onChange={(e) => {
                      setProfile1(e.target.value)
                      // Clear error when user starts typing
                      if (errors.profile1) {
                        setErrors(prev => ({ ...prev, profile1: undefined }))
                      }
                    }}
                    className={`pl-12 bg-white/5 border-red-500/20 text-white placeholder:text-white/50 rounded-xl h-14 text-lg focus:border-red-400 ${errors.profile1 ? 'border-red-500' : ''
                      }`}
                  />
                </div>
                {errors.profile1 && (
                  <p className="text-red-400 text-sm mt-1">{errors.profile1}</p>
                )}
              </div>

              {/* Profile 2 */}
              <div className="space-y-3">
                <Label htmlFor="profile2" className="text-white font-medium flex items-center gap-2">
                  <div className="w-6 h-6 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center">
                    <User className="w-3 h-3 text-white" />
                  </div>
                  Second Profile
                </Label>
                <div className="relative">
                  <LinkIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/50" />
                  <Input
                    id="profile2"
                    type="url"
                    placeholder="Username"
                    value={profile2}
                    onChange={(e) => {
                      setProfile2(e.target.value)
                      // Clear error when user starts typing
                      if (errors.profile2) {
                        setErrors(prev => ({ ...prev, profile2: undefined }))
                      }
                    }}
                    className={`pl-12 bg-white/5 border-red-500/20 text-white placeholder:text-white/50 rounded-xl h-14 text-lg focus:border-red-400 ${errors.profile2 ? 'border-red-500' : ''
                      }`}
                  />
                </div>
                {errors.profile2 && (
                  <p className="text-red-400 text-sm mt-1">{errors.profile2}</p>
                )}
              </div>

              {/* Blend Button */}
              <motion.div className="pt-4" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  onClick={handleBlend}
                  disabled={!profile1 || !profile2 || isLoading}
                  className="w-full bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white py-6 text-lg rounded-xl shadow-2xl hover:shadow-red-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <motion.div className="flex items-center gap-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                      <motion.div
                        className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                      />
                      Blending your tastes...
                    </motion.div>
                  ) : (
                    <>
                      Create Movie Blend
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </>
                  )}
                </Button>
              </motion.div>

              {/* Mock Data Button */}
              <motion.div className="pt-2" whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                <Button
                  onClick={handleMockBlend}
                  disabled={isLoading}
                  variant="outline"
                  className="w-full border-red-500/30 text-white hover:bg-red-500/10 py-4 text-sm rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed bg-transparent"
                >
                  {isLoading ? (
                    <motion.div className="flex items-center gap-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                      <motion.div
                        className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
                      />
                      Loading data...
                    </motion.div>
                  ) : (
                    <>
                      Use Example Profiles
                    </>
                  )}
                </Button>
              </motion.div>
            </div>
          </motion.div>

          {/* Example */}
          <motion.div
            className="mt-12 text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="text-white/60 text-sm mb-2">Example format:</p>
            <code className="text-white/80 bg-white/10 px-4 py-2 rounded-lg text-sm">
              vihaanbinges
            </code>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
