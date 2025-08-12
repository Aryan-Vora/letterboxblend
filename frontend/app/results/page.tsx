"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Film, Star, Calendar, ArrowLeft, Share2 } from "lucide-react"
import Link from "next/link"
import Image from "next/image"

export default function ResultsPage() {
  const [movies, setMovies] = useState<any[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isRevealing, setIsRevealing] = useState(true)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Load results from localStorage
    const storedResults = localStorage.getItem('blendResults')

    if (storedResults) {
      try {
        const results = JSON.parse(storedResults)
        setMovies(results)
        setIsLoading(false)
      } catch (error) {
        setIsLoading(false)
      }
    } else {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {

    if (!isLoading && isRevealing && currentIndex < movies.length) {
      const timer = setTimeout(() => {
        setCurrentIndex((prev) => {
          return prev + 1
        })
      }, 800)
      return () => clearTimeout(timer)
    } else if (currentIndex >= movies.length && movies.length > 0) {
      setIsRevealing(false)
    }
  }, [currentIndex, isRevealing, movies.length, isLoading])

  const getRankColor = (index: number) => {
    if (index < 3) return "from-red-400 to-orange-500"
    if (index < 10) return "from-orange-400 to-red-500"
    if (index < 20) return "from-red-500 to-red-600"
    return "from-red-600 to-orange-600"
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-red-950 to-gray-900 overflow-hidden">
      {/* Animated background */}
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
          className="absolute bottom-32 right-32 w-40 h-40 bg-orange-500/20 rounded-full blur-xl"
          animate={{
            x: [0, -80, 0],
            y: [0, 60, 0],
            scale: [1, 0.8, 1],
          }}
          transition={{
            duration: 10,
            repeat: Number.POSITIVE_INFINITY,
            ease: "easeInOut",
          }}
        />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <motion.header
          className="flex items-center justify-between mb-12"
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
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              className="border-red-500/20 text-white hover:bg-red-500/10 bg-transparent"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Share Blend
            </Button>
            <Link href="/blend">
              <Button
                variant="outline"
                size="sm"
                className="border-red-500/20 text-white hover:bg-red-500/10 bg-transparent"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                New Blend
              </Button>
            </Link>
          </div>
        </motion.header>

        {/* Title */}
        <motion.div
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-red-400 via-orange-400 to-red-500 bg-clip-text text-transparent">
            Your Movie Blend
          </h1>
          <p className="text-xl text-white/80">
            {isLoading ? "Loading your recommendations..." : `Top ${movies.length} movies you'll both love`}
          </p>
        </motion.div>

        {/* Movies Grid */}
        <div className="grid gap-6 max-w-6xl mx-auto">
          {isLoading ? (
            <motion.div
              className="flex items-center justify-center py-24"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <motion.div
                className="w-8 h-8 border-2 border-red-500/30 border-t-red-500 rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
              />
              <span className="ml-3 text-white/80">Loading your movie blend...</span>
            </motion.div>
          ) : movies.length === 0 ? (
            <motion.div
              className="text-center py-24"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <h2 className="text-2xl font-bold text-white mb-4">No recommendations found</h2>
              <p className="text-white/70 mb-8">Please try creating a new blend with different profiles.</p>
              <Link href="/blend">
                <Button className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-8 py-3 rounded-xl">
                  Try Again
                </Button>
              </Link>
            </motion.div>
          ) : (
            <AnimatePresence>
              {movies.slice(0, currentIndex).map((movie, index) => (
                <motion.div
                  key={movie.title || index}
                  className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-red-500/20 shadow-2xl"
                  initial={{ opacity: 0, y: 50, scale: 0.9 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{
                    duration: 0.6,
                    delay: index * 0.1,
                    ease: "easeOut",
                  }}
                  layout
                >
                  <div className="flex flex-col md:flex-row gap-6">
                    {/* Rank */}
                    <div className="flex-shrink-0">
                      <motion.div
                        className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${getRankColor(index)} flex items-center justify-center shadow-lg`}
                        whileHover={{ scale: 1.1 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        <span className="text-2xl font-bold text-white">#{index + 1}</span>
                      </motion.div>
                    </div>

                    {/* Movie Poster */}
                    <div className="flex-shrink-0">
                      <motion.div
                        className="w-24 h-36 rounded-xl overflow-hidden shadow-lg bg-white/10"
                        whileHover={{ scale: 1.05 }}
                        transition={{ type: "spring", stiffness: 300 }}
                      >
                        {movie.thumbnail ? (
                          <Image
                            src={movie.thumbnail}
                            alt={movie.title}
                            width={96}
                            height={144}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-white/50">
                            <Film className="w-8 h-8" />
                          </div>
                        )}
                      </motion.div>
                    </div>

                    {/* Movie Info */}
                    <div className="flex-1 space-y-4">
                      <div>
                        <h3 className="text-2xl font-bold text-white mb-2">{movie.title}</h3>
                        <div className="flex flex-wrap items-center gap-4 text-white/70 text-sm">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {movie.year}
                          </div>
                          {movie.cast && movie.cast.length > 0 && (
                            <Badge variant="secondary" className="bg-red-500/20 text-white border-0">
                              {movie.cast.slice(0, 3).join(', ')}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {movie.extract && (
                        <p className="text-white/80 leading-relaxed line-clamp-2">{movie.extract}</p>
                      )}

                      <div className="flex flex-wrap items-center gap-4">
                        <div className="flex items-center gap-2">
                          <Star className="w-5 h-5 text-orange-400 fill-current" />
                          <span className="text-white font-semibold">{movie.rating?.toFixed(1) || 'N/A'}</span>
                          <span className="text-white/60 text-sm">IMDb</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-5 h-5 bg-gradient-to-r from-red-400 to-orange-500 rounded flex items-center justify-center">
                            <span className="text-white text-xs font-bold">B</span>
                          </div>
                          <span className="text-white font-semibold">{movie.combined_score?.toFixed(1) || 'N/A'}</span>
                          <span className="text-white/60 text-sm">Blend Score</span>
                        </div>
                      </div>

                      {movie.genres && movie.genres.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {movie.genres.slice(0, 4).map((genre: string) => (
                            <Badge
                              key={genre}
                              variant="outline"
                              className="border-red-500/30 text-white/80 hover:bg-red-500/10"
                            >
                              {genre}
                            </Badge>
                          ))}
                        </div>
                      )}

                      <div className="grid grid-cols-2 gap-4 text-sm text-white/60">
                        <div>
                          <span className="text-white/80 font-medium">Genre Score:</span> {movie.genre_score?.toFixed(2) || 'N/A'}
                        </div>
                        <div>
                          <span className="text-white/80 font-medium">Plot Score:</span> {movie.plot_score?.toFixed(2) || 'N/A'}
                        </div>
                        <div>
                          <span className="text-white/80 font-medium">Actor Score:</span> {movie.actor_score?.toFixed(2) || 'N/A'}
                        </div>
                        <div>
                          <span className="text-white/80 font-medium">IMDb Bonus:</span> {movie.imdb_bonus?.toFixed(2) || 'N/A'}
                        </div>
                        <div>
                          <span className="text-white/80 font-medium">Recency Bonus:</span> {movie.recency_bonus?.toFixed(2) || 'N/A'}
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}

          {/* Loading indicator */}
          {!isLoading && isRevealing && currentIndex < movies.length && (
            <motion.div
              className="flex items-center justify-center py-12"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div
                className="w-8 h-8 border-2 border-red-500/30 border-t-red-500 rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Number.POSITIVE_INFINITY, ease: "linear" }}
              />
              <span className="ml-3 text-white/80">Revealing your next match...</span>
            </motion.div>
          )}
        </div>

        {/* Completion message */}
        {!isRevealing && (
          <motion.div
            className="text-center mt-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-3xl font-bold text-white mb-4">🎬 Your blend is complete!</h2>
            <p className="text-white/80 mb-8">These are the movies that perfectly match both of your tastes</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/blend">
                <Button className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white px-8 py-3 rounded-xl">
                  Create Another Blend
                </Button>
              </Link>
              <Button
                variant="outline"
                className="border-red-500/20 text-white hover:bg-red-500/10 px-8 py-3 rounded-xl bg-transparent"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share Results
              </Button>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
