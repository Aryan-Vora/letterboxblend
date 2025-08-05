"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Film, Users, Heart, Sparkles, Zap } from "lucide-react"
import { useEffect } from "react"
import Link from "next/link"

export default function HomePage() {
  // hack to get render out of cold start
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}`)
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.error("Error fetching API:", error))
  }, [])
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-red-950 to-gray-900 overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0">
        <motion.div
          className="absolute top-20 left-20 w-32 h-32 bg-red-500/20 rounded-full blur-xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 8,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute top-40 right-32 w-24 h-24 bg-orange-500/20 rounded-full blur-xl"
          animate={{
            x: [0, -80, 0],
            y: [0, 60, 0],
            scale: [1, 0.8, 1],
          }}
          transition={{
            duration: 6,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute bottom-32 left-1/3 w-40 h-40 bg-red-600/20 rounded-full blur-xl"
          animate={{
            x: [0, 60, 0],
            y: [0, -40, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 10,
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
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-r from-red-500 to-red-600 rounded-lg flex items-center justify-center">
              <Film className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">MovieBlend</span>
          </div>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="#how-it-works" className="text-white/80 hover:text-white transition-colors">
              How it works
            </Link>
            <Link href="#about" className="text-white/80 hover:text-white transition-colors">
              About
            </Link>
          </nav>
        </motion.header>

        {/* Hero Section */}
        <div className="text-center max-w-4xl mx-auto">
          <motion.div
            className="mb-8"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2 mb-6">
              <Sparkles className="w-4 h-4 text-red-400" />
              <span className="text-white/90 text-sm">Discover your perfect movie match</span>
            </div>

            <motion.h1
              className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-red-400 via-orange-400 to-red-500 bg-clip-text text-transparent"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              Movie Blend
            </motion.h1>

            <motion.p
              className="text-xl md:text-2xl text-white/80 mb-12 leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              Blend your Letterboxd tastes with a friend and discover
              <br />
              <span className="bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent font-semibold">
                movies you'll both love
              </span>
            </motion.p>
          </motion.div>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <Link href="/blend">
              <Button
                size="lg"
                className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-12 py-6 text-lg rounded-full shadow-2xl hover:shadow-red-500/25 transition-all duration-300 transform hover:scale-105"
              >
                <Users className="w-5 h-5 mr-2" />
                Start Blending
              </Button>
            </Link>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            className="grid md:grid-cols-3 gap-8 mt-24"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1 }}
          >
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20">
              <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Perfect Matches</h3>
              <p className="text-white/70">
                Our algorithm analyzes your Letterboxd profiles to find movies that both you and your friend will love.
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Smart Blending</h3>
              <p className="text-white/70">
                We analyze your viewing history, ratings, and preferences to create the perfect movie blend using
                advanced algorithms.
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20">
              <div className="w-12 h-12 bg-gradient-to-r from-red-600 to-orange-600 rounded-xl flex items-center justify-center mb-4 mx-auto">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">Instant Discovery</h3>
              <p className="text-white/70">
                Get personalized recommendations in seconds and discover hidden gems that align with both your tastes.
              </p>
            </div>
          </motion.div>

          {/* How It Works Section */}
          <motion.section
            id="how-it-works"
            className="mt-32 mb-24"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-red-400 via-orange-400 to-red-500 bg-clip-text text-transparent">
                How It Works
              </h2>
              <p className="text-xl text-white/80 max-w-3xl mx-auto">
                Our sophisticated algorithm analyzes your movie preferences to create the perfect blend
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
              <motion.div
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20 relative overflow-hidden"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-red-500/20 to-orange-500/20 rounded-full blur-xl" />
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-xl flex items-center justify-center mb-6">
                    <span className="text-white font-bold text-xl">1</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-4">Analyze Your Tastes</h3>
                  <p className="text-white/70 leading-relaxed">
                    We examine your Letterboxd profiles to understand your favorite genres, preferred time periods,
                    beloved actors, and rating patterns.
                  </p>
                </div>
              </motion.div>

              <motion.div
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20 relative overflow-hidden"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-orange-500/20 to-red-600/20 rounded-full blur-xl" />
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl flex items-center justify-center mb-6">
                    <span className="text-white font-bold text-xl">2</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-4">Find Common Ground</h3>
                  <p className="text-white/70 leading-relaxed">
                    Our algorithm identifies shared preferences between both users - common genres, overlapping year
                    ranges, and mutual favorite actors.
                  </p>
                </div>
              </motion.div>

              <motion.div
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20 relative overflow-hidden"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-red-600/20 to-orange-600/20 rounded-full blur-xl" />
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-red-600 to-orange-500 rounded-xl flex items-center justify-center mb-6">
                    <span className="text-white font-bold text-xl">3</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-4">Smart Genre Weighting</h3>
                  <p className="text-white/70 leading-relaxed">
                    We weight genres based on how many movies each user has watched in that category and their average
                    ratings, prioritizing your strongest shared interests.
                  </p>
                </div>
              </motion.div>

              <motion.div
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20 relative overflow-hidden"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-orange-600/20 to-red-700/20 rounded-full blur-xl" />
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-orange-600 to-red-600 rounded-xl flex items-center justify-center mb-6">
                    <span className="text-white font-bold text-xl">4</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-4">Quality Filtering</h3>
                  <p className="text-white/70 leading-relaxed">
                    We filter out low-rated movies (under 5.0) and exclude films you've both already seen, ensuring
                    fresh, high-quality recommendations.
                  </p>
                </div>
              </motion.div>

              <motion.div
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20 relative overflow-hidden"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-red-700/20 to-orange-700/20 rounded-full blur-xl" />
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-red-700 to-orange-600 rounded-xl flex items-center justify-center mb-6">
                    <span className="text-white font-bold text-xl">5</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-4">Similarity Matching</h3>
                  <p className="text-white/70 leading-relaxed">
                    Using advanced similarity search, we match movie plots and themes with your viewing history to find
                    films that truly resonate with both of you.
                  </p>
                </div>
              </motion.div>

              <motion.div
                className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20 relative overflow-hidden"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-orange-700/20 to-red-800/20 rounded-full blur-xl" />
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-r from-orange-700 to-red-700 rounded-xl flex items-center justify-center mb-6">
                    <span className="text-white font-bold text-xl">6</span>
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-4">Perfect Ranking</h3>
                  <p className="text-white/70 leading-relaxed">
                    Finally, we rank your matches by the highest ratings and popularity, delivering a personalized list
                    of movies you'll both absolutely love.
                  </p>
                </div>
              </motion.div>
            </div>
          </motion.section>

          {/* About Section */}
          <motion.section
            id="about"
            className="mt-32 mb-24"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.4 }}
          >
            <div className="max-w-4xl mx-auto">
              <div className="text-center mb-16">
                <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-orange-400 via-red-400 to-red-500 bg-clip-text text-transparent">
                  About MovieBlend
                </h2>
                <p className="text-xl text-white/80">Bringing movie lovers together, one perfect match at a time</p>
              </div>

              <div className="grid md:grid-cols-2 gap-12 items-center">
                <motion.div
                  className="space-y-6"
                  whileHover={{ scale: 1.02 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20">
                    <h3 className="text-2xl font-bold text-white mb-4">Our Mission</h3>
                    <p className="text-white/80 leading-relaxed mb-4">
                      We believe that the best movie experiences happen when shared with others. MovieBlend was created
                      to solve the age-old problem: "What should we watch tonight?"
                    </p>
                    <p className="text-white/80 leading-relaxed">
                      By analyzing your Letterboxd profiles with sophisticated algorithms, we eliminate the guesswork
                      and deliver personalized recommendations that both you and your movie partner will love.
                    </p>
                  </div>
                </motion.div>

                <motion.div
                  className="space-y-6"
                  whileHover={{ scale: 1.02 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20">
                    <h3 className="text-2xl font-bold text-white mb-4">The Science Behind the Magic</h3>
                    <p className="text-white/80 leading-relaxed mb-4">
                      Our algorithm doesn't just look at what you've watched - it understands <em>how</em> you watch. We
                      analyze:
                    </p>
                    <ul className="space-y-2 text-white/70">
                      <li className="flex items-start gap-2">
                        <div className="w-2 h-2 bg-gradient-to-r from-red-400 to-orange-400 rounded-full mt-2 flex-shrink-0" />
                        Genre preferences weighted by viewing frequency and ratings
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-2 h-2 bg-gradient-to-r from-orange-400 to-red-500 rounded-full mt-2 flex-shrink-0" />
                        Temporal patterns in your movie choices
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-2 h-2 bg-gradient-to-r from-red-500 to-red-600 rounded-full mt-2 flex-shrink-0" />
                        Actor and director affinities across both profiles
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-2 h-2 bg-gradient-to-r from-red-600 to-orange-600 rounded-full mt-2 flex-shrink-0" />
                        Semantic similarity between movie plots and themes
                      </li>
                    </ul>
                  </div>
                </motion.div>
              </div>

              <motion.div
                className="mt-12 bg-gradient-to-r from-red-500/20 to-orange-500/20 backdrop-blur-sm rounded-2xl p-8 border border-red-500/20 text-center"
                whileHover={{ scale: 1.02 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                <h3 className="text-2xl font-bold text-white mb-4">Built for Movie Lovers, by Movie Lovers</h3>
                <p className="text-white/80 leading-relaxed max-w-2xl mx-auto">
                  We're passionate cinephiles who understand that great movies are meant to be shared. Whether you're
                  planning a date night, a movie marathon with friends, or just trying to find something everyone can
                  agree on, MovieBlend takes the stress out of choosing and puts the joy back into watching.
                </p>
              </motion.div>
            </div>
          </motion.section>

          {/* Stats Section */}
          <motion.section
            className="mt-32 mb-16"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 1.6 }}
          >
            <div className="grid md:grid-cols-4 gap-8 max-w-4xl mx-auto">
              <div className="text-center">
                <motion.div
                  className="text-4xl font-bold bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent mb-2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.6, delay: 1.8 }}
                >
                  50K+
                </motion.div>
                <p className="text-white/70">Movies Analyzed</p>
              </div>
              <div className="text-center">
                <motion.div
                  className="text-4xl font-bold bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent mb-2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.6, delay: 2.0 }}
                >
                  5+
                </motion.div>
                <p className="text-white/70">Happy Users</p>
              </div>
              <div className="text-center">
                <motion.div
                  className="text-4xl font-bold bg-gradient-to-r from-red-500 to-red-600 bg-clip-text text-transparent mb-2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.6, delay: 2.2 }}
                >
                  95%
                </motion.div>
                <p className="text-white/70">Match Accuracy</p>
              </div>
              <div className="text-center">
                <motion.div
                  className="text-4xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent mb-2"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.6, delay: 2.4 }}
                >
                  24/7
                </motion.div>
                <p className="text-white/70">Always Available</p>
              </div>
            </div>
          </motion.section>
        </div>
      </div>
    </div>
  )
}
