import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Dimensions,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';
import { WebView } from 'react-native-webview';
import axios from 'axios';

const { width, height } = Dimensions.get('window');

// Coordinates
const Delhi = { latitude: 28.6139, longitude: 77.2090 };
const Mandi = { latitude: 31.7333, longitude: 76.9333 };

// Map component using OpenStreetMap via WebView
const MapSection = ({ showResults }) => {
  const [routeCoordinates, setRouteCoordinates] = useState([]);
  const [mapHTML, setMapHTML] = useState('');

  useEffect(() => {
    if (!showResults) return;

    const fetchRoute = async () => {
      try {
        const response = await axios.get(
          `https://router.project-osrm.org/route/v1/driving/${Delhi.longitude},${Delhi.latitude};${Mandi.longitude},${Mandi.latitude}?geometries=geojson`
        );

        const coords = response.data.routes[0].geometry.coordinates;
        setRouteCoordinates(coords);
        
        // Generate HTML for OpenStreetMap with Leaflet
        const html = generateMapHTML(coords);
        setMapHTML(html);
      } catch (error) {
        console.error('Error fetching route:', error);
        // Generate map without route if API fails
        const html = generateMapHTML([]);
        setMapHTML(html);
      }
    };

    fetchRoute();
  }, [showResults]);

  const generateMapHTML = (routeCoords) => {
    const routePolyline = routeCoords.length > 0 
      ? `var routeCoords = ${JSON.stringify(routeCoords.map(c => [c[1], c[0]]))};
         var polyline = L.polyline(routeCoords, {color: '#2E7D32', weight: 4}).addTo(map);`
      : '';

    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
          body { margin: 0; padding: 0; }
          #map { width: 100%; height: 100vh; }
        </style>
      </head>
      <body>
        <div id="map"></div>
        <script>
          var map = L.map('map').setView([${(Delhi.latitude + Mandi.latitude) / 2}, ${(Delhi.longitude + Mandi.longitude) / 2}], 7);
          
          L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
          }).addTo(map);
          
          var delhiMarker = L.marker([${Delhi.latitude}, ${Delhi.longitude}]).addTo(map);
          delhiMarker.bindPopup('<b>Delhi</b>').openPopup();
          
          var mandiMarker = L.marker([${Mandi.latitude}, ${Mandi.longitude}]).addTo(map);
          mandiMarker.bindPopup('<b>Mandi</b>');
          
          ${routePolyline}
          
          ${routeCoords.length > 0 ? 'map.fitBounds(polyline.getBounds(), {padding: [50, 50]});' : ''}
        </script>
      </body>
      </html>
    `;
  };

  if (!showResults) return null;

  return (
    <Animatable.View animation="fadeInUp" style={styles.mapContainer}>
      {mapHTML ? (
        <WebView
          originWhitelist={['*']}
          source={{ html: mapHTML }}
          style={styles.map}
          javaScriptEnabled={true}
          domStorageEnabled={true}
          allowFileAccess={true}
          allowUniversalAccessFromFileURLs={true}
          mixedContentMode="always"
          onError={(syntheticEvent) => {
            const { nativeEvent } = syntheticEvent;
            console.warn('WebView error: ', nativeEvent);
          }}
        />
      ) : (
        <View style={styles.mapPlaceholder}>
          <Icon name="map" size={40} color="#2E7D32" />
          <Text style={styles.mapPlaceholderText}>Loading map...</Text>
        </View>
      )}
    </Animatable.View>
  );
};

const HomeScreen = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [progressMessage, setProgressMessage] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [isListening, setIsListening] = useState(false);

  const progressMessages = [
    'Fetching data...',
    'Understanding context...',
    'Analyzing traffic patterns...',
    'Optimizing route...',
    'Calculating environmental factors...',
    'Finalizing recommendations...',
  ];

  const handleSearch = () => {
    if (searchQuery.trim()) {
      setIsSearching(true);
      setShowResults(false);
      let messageIndex = 0;

      const progressInterval = setInterval(() => {
        setProgressMessage(progressMessages[messageIndex]);
        messageIndex++;

        if (messageIndex >= progressMessages.length) {
          clearInterval(progressInterval);
          setTimeout(() => {
            setIsSearching(false);
            setShowResults(true);
          }, 1000);
        }
      }, 1500);
    }
  };

  const handleVoiceInput = () => {
    setIsListening(true);
    setTimeout(() => {
      setSearchQuery('I want to go from Delhi to Mandi having greenery');
      setIsListening(false);
    }, 2000);
  };

  const renderProgressOverlay = () => {
    if (!isSearching) return null;

    return (
      <View style={styles.progressOverlay}>
        <LinearGradient
          colors={['rgba(46, 125, 50, 0.95)', 'rgba(76, 175, 80, 0.95)']}
          style={styles.progressContainer}
        >
          <Animatable.View animation="pulse" iterationCount="infinite">
            <Icon name="search" size={40} color="#FFFFFF" />
          </Animatable.View>
          <Text style={styles.progressText}>{progressMessage}</Text>
          <View style={styles.progressBar}>
            <Animatable.View
              animation="slideInLeft"
              iterationCount="infinite"
              style={styles.progressBarFill}
            />
          </View>
        </LinearGradient>
      </View>
    );
  };

  const renderInfoCards = () => {
    if (!showResults) return null;

    const cards = [
      {
        title: 'Air Quality Index',
        value: 'Good',
        icon: 'air',
        color: '#4CAF50',
        details: 'PM2.5: 25 μg/m³',
      },
      {
        title: 'Noise Level',
        value: 'Moderate',
        icon: 'volume-up',
        color: '#FF9800',
        details: '65 dB',
      },
      {
        title: 'Greenery Index',
        value: 'High',
        icon: 'park',
        color: '#2E7D32',
        details: '85% Green Coverage',
      },
      {
        title: 'Travel Time',
        value: '6h 30m',
        icon: 'schedule',
        color: '#2196F3',
        details: 'Via NH44',
      },
    ];

    return (
      <Animatable.View animation="fadeInUp" delay={500} style={styles.cardsContainer}>
        {cards.map((card, index) => (
          <Animatable.View
            key={index}
            animation="fadeInUp"
            delay={700 + index * 100}
            style={[styles.card, { borderLeftColor: card.color }]}
          >
            <View style={styles.cardHeader}>
              <Icon name={card.icon} size={24} color={card.color} />
              <Text style={styles.cardTitle}>{card.title}</Text>
            </View>
            <Text style={[styles.cardValue, { color: card.color }]}>{card.value}</Text>
            <Text style={styles.cardDetails}>{card.details}</Text>
          </Animatable.View>
        ))}
      </Animatable.View>
    );
  };

  const renderTravelNews = () => {
    const newsItems = [
      {
        title: 'New Green Corridor Opens in Delhi',
        summary: 'Dedicated cycling lanes connecting major parks',
        time: '2 hours ago',
      },
      {
        title: 'Mandi Tourism Booms with Eco-Friendly Initiatives',
        summary: 'Local government promotes sustainable travel',
        time: '4 hours ago',
      },
      {
        title: 'Weather Alert: Pleasant Conditions Expected',
        summary: 'Perfect weather for outdoor activities',
        time: '6 hours ago',
      },
    ];

    return (
      <View style={styles.newsContainer}>
        <Text style={styles.newsTitle}>Travel Updates</Text>
        {newsItems.map((item, index) => (
          <Animatable.View
            key={index}
            animation="fadeInRight"
            delay={index * 200}
            style={styles.newsItem}
          >
            <View style={styles.newsContent}>
              <Text style={styles.newsItemTitle}>{item.title}</Text>
              <Text style={styles.newsItemSummary}>{item.summary}</Text>
              <Text style={styles.newsItemTime}>{item.time}</Text>
            </View>
            <Icon name="chevron-right" size={20} color="#666" />
          </Animatable.View>
        ))}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#E8F5E8', '#F0F8F0']} style={styles.gradient}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>UrbanPulse+</Text>
          <Text style={styles.headerSubtitle}>Smart Travel Assistant</Text>
        </View>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <View style={styles.searchBar}>
            <Icon name="search" size={20} color="#666" />
            <TextInput
              style={styles.searchInput}
              placeholder="Where do you want to go?"
              value={searchQuery}
              onChangeText={setSearchQuery}
              onSubmitEditing={handleSearch}
            />
            <TouchableOpacity
              style={[styles.voiceButton, isListening && styles.voiceButtonActive]}
              onPress={handleVoiceInput}
              disabled={isListening}
            >
              <Icon
                name={isListening ? 'mic' : 'mic-none'}
                size={20}
                color={isListening ? '#FFFFFF' : '#666'}
              />
            </TouchableOpacity>
          </View>
          <TouchableOpacity
            style={[styles.searchButton, isSearching && styles.searchButtonDisabled]}
            onPress={handleSearch}
            disabled={isSearching}
          >
            <Text style={styles.searchButtonText}>
              {isSearching ? 'Searching...' : 'Search'}
            </Text>
          </TouchableOpacity>
        </View>

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          <MapSection showResults={showResults} />
          {renderInfoCards()}
          {!showResults && renderTravelNews()}
        </ScrollView>

        {renderProgressOverlay()}
      </LinearGradient>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  gradient: { flex: 1 },
  header: { paddingHorizontal: 20, paddingTop: 20, paddingBottom: 10 },
  headerTitle: { fontSize: 28, fontWeight: 'bold', color: '#2E7D32' },
  headerSubtitle: { fontSize: 16, color: '#666', marginTop: 5 },
  searchContainer: { paddingHorizontal: 20, marginBottom: 20 },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 25,
    paddingHorizontal: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  searchInput: { flex: 1, paddingVertical: 15, paddingHorizontal: 10, fontSize: 16, color: '#333' },
  voiceButton: {
    backgroundColor: '#F5F5F5',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  voiceButtonActive: { backgroundColor: '#2E7D32' },
  searchButton: { backgroundColor: '#2E7D32', borderRadius: 25, paddingVertical: 15, alignItems: 'center' },
  searchButtonDisabled: { backgroundColor: '#A5D6A7' },
  searchButtonText: { color: '#FFFFFF', fontSize: 16, fontWeight: 'bold' },
  content: { flex: 1, paddingHorizontal: 20 },

  // Map
  mapContainer: {
    height: 250,
    borderRadius: 15,
    overflow: 'hidden',
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 8,
    backgroundColor: '#FFFFFF',
  },
  map: { flex: 1 },
  mapPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  mapPlaceholderText: {
    marginTop: 10,
    fontSize: 14,
    color: '#666',
  },

  // Cards
  cardsContainer: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', marginBottom: 20 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 15,
    width: (width - 60) / 2,
    marginBottom: 10,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  cardTitle: { fontSize: 14, color: '#666', marginLeft: 8, flex: 1 },
  cardValue: { fontSize: 18, fontWeight: 'bold', marginBottom: 4 },
  cardDetails: { fontSize: 12, color: '#999' },

  // News
  newsContainer: { backgroundColor: '#FFFFFF', borderRadius: 15, padding: 20, marginBottom: 20, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 4 },
  newsTitle: { fontSize: 20, fontWeight: 'bold', color: '#2E7D32', marginBottom: 15 },
  newsItem: { flexDirection: 'row', alignItems: 'center', paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: '#F0F0F0' },
  newsContent: { flex: 1 },
  newsItemTitle: { fontSize: 16, fontWeight: '600', color: '#333', marginBottom: 4 },
  newsItemSummary: { fontSize: 14, color: '#666', marginBottom: 4 },
  newsItemTime: { fontSize: 12, color: '#999' },

  // Progress overlay
  progressOverlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, justifyContent: 'center', alignItems: 'center', zIndex: 1000 },
  progressContainer: { backgroundColor: 'rgba(46, 125, 50, 0.95)', borderRadius: 20, padding: 40, alignItems: 'center', minWidth: 250 },
  progressText: { color: '#FFFFFF', fontSize: 18, fontWeight: 'bold', marginTop: 20, textAlign: 'center' },
  progressBar: { width: 200, height: 4, backgroundColor: 'rgba(255, 255, 255, 0.3)', borderRadius: 2, marginTop: 20, overflow: 'hidden' },
  progressBarFill: { height: '100%', backgroundColor: '#FFFFFF', borderRadius: 2, width: '30%' },
});

export default HomeScreen;