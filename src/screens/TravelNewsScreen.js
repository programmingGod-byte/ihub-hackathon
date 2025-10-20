import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Image,
  RefreshControl,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import LinearGradient from 'react-native-linear-gradient';
import * as Animatable from 'react-native-animatable';

const TravelNewsScreen = () => {
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'All', icon: 'apps' },
    { id: 'environment', name: 'Environment', icon: 'eco' },
    { id: 'safety', name: 'Safety', icon: 'security' },
    { id: 'traffic', name: 'Traffic', icon: 'traffic' },
    { id: 'weather', name: 'Weather', icon: 'wb-sunny' },
  ];

  // --- Added realistic, themed image URLs ---
  const newsData = [
    {
      id: 1,
      title: 'New Green Corridor Opens in Delhi',
      summary:
        'Dedicated cycling lanes connecting major parks and green spaces across the capital city.',
      content:
        'The Delhi government has inaugurated a new 15km green corridor connecting Lodhi Gardens to Central Park. This initiative aims to promote eco-friendly transportation and reduce carbon emissions in the city.',
      category: 'environment',
      author: 'Delhi Transport Authority',
      publishTime: '2 hours ago',
      readTime: '3 min read',
      image:
        'https://images.unsplash.com/photo-1602407294553-68e1a74691dd?auto=format&fit=crop&w=800&q=60',
      tags: ['Green Transport', 'Delhi', 'Cycling'],
      likes: 124,
      comments: 23,
      isBookmarked: false,
    },
    {
      id: 2,
      title: 'Mandi Tourism Booms with Eco-Friendly Initiatives',
      summary:
        'Local government promotes sustainable travel with new eco-tourism packages.',
      content:
        'Mandi district has launched several eco-friendly tourism initiatives including electric vehicle rentals, solar-powered accommodations, and guided nature walks through pristine forests.',
      category: 'environment',
      author: 'Himachal Tourism Board',
      publishTime: '4 hours ago',
      readTime: '4 min read',
      image:
        'https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=800&q=60',
      tags: ['Eco Tourism', 'Mandi', 'Sustainability'],
      likes: 89,
      comments: 15,
      isBookmarked: true,
    },
    {
      id: 3,
      title: 'Weather Alert: Pleasant Conditions Expected',
      summary:
        'Perfect weather forecast for outdoor activities and travel across northern India.',
      content:
        'Meteorological department predicts clear skies and comfortable temperatures for the next week, making it ideal for road trips and outdoor adventures.',
      category: 'weather',
      author: 'India Meteorological Department',
      publishTime: '6 hours ago',
      readTime: '2 min read',
      image:
        'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=60',
      tags: ['Weather', 'Travel', 'Forecast'],
      likes: 67,
      comments: 8,
      isBookmarked: false,
    },
    {
      id: 4,
      title: 'Enhanced Safety Measures on NH44',
      summary:
        'New safety installations and improved lighting on the Delhi-Mandi highway route.',
      content:
        'The National Highways Authority has installed advanced safety barriers, improved street lighting, and emergency response stations along the NH44 corridor.',
      category: 'safety',
      author: 'National Highways Authority',
      publishTime: '8 hours ago',
      readTime: '3 min read',
      image:
        'https://images.unsplash.com/photo-1587740896339-2e6d1a6936fc?auto=format&fit=crop&w=800&q=60',
      tags: ['Safety', 'NH44', 'Highway'],
      likes: 156,
      comments: 31,
      isBookmarked: true,
    },
    {
      id: 5,
      title: 'Traffic Optimization in Major Cities',
      summary:
        'Smart traffic management systems reduce congestion by 30% in urban areas.',
      content:
        'AI-powered traffic management systems have been successfully implemented in major cities, resulting in significant reduction in traffic congestion and improved air quality.',
      category: 'traffic',
      author: 'Smart City Initiative',
      publishTime: '12 hours ago',
      readTime: '5 min read',
      image:
        'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=800&q=60',
      tags: ['Smart City', 'AI', 'Traffic Management'],
      likes: 203,
      comments: 45,
      isBookmarked: false,
    },
    {
      id: 6,
      title: 'Electric Vehicle Charging Stations Expand',
      summary:
        'New EV charging infrastructure makes long-distance electric travel more feasible.',
      content:
        'Over 200 new electric vehicle charging stations have been installed along major highways, making electric vehicle travel more convenient and accessible.',
      category: 'environment',
      author: 'Electric Vehicle Council',
      publishTime: '1 day ago',
      readTime: '4 min read',
      image:
        'https://images.unsplash.com/photo-1615906658185-10233b1b87b7?auto=format&fit=crop&w=800&q=60',
      tags: ['Electric Vehicles', 'Infrastructure', 'Sustainability'],
      likes: 178,
      comments: 29,
      isBookmarked: true,
    },
  ];

  const filteredNews =
    selectedCategory === 'all'
      ? newsData
      : newsData.filter((item) => item.category === selectedCategory);

  const onRefresh = () => {
    setRefreshing(true);
    setTimeout(() => {
      setRefreshing(false);
    }, 2000);
  };

  const toggleBookmark = (id) => {
    console.log('Toggle bookmark for article:', id);
  };

  const renderCategoryFilter = () => (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      >
      {categories.map((category, index) => (
        <Animatable.View
          key={category.id}
          animation="fadeInRight"
          duration={500}
          delay={index * 100}>
          <TouchableOpacity
            activeOpacity={0.8}
            style={[
              styles.categoryButtonNew,
              selectedCategory === category.id && styles.categoryButtonNewActive,
            ]}
            onPress={() => setSelectedCategory(category.id)}>
            <Icon
              name={category.icon}
              size={18}
              color={selectedCategory === category.id ? '#fff' : '#2E7D32'}
            />
            <Text
              style={[
                styles.categoryTextNew,
                selectedCategory === category.id && styles.categoryTextNewActive,
              ]}>
              {category.name}
            </Text>
          </TouchableOpacity>
        </Animatable.View>
      ))}
    </ScrollView>
  );

  const renderNewsCard = (item, index) => (
    <Animatable.View
      key={item.id}
      animation="fadeInUp"
      delay={index * 120}
      style={styles.newsCard}>
      <View style={styles.newsImageContainer}>
        <Image source={{ uri: item.image }} style={styles.newsImage} />
        <LinearGradient
          colors={['transparent', 'rgba(0,0,0,0.5)']}
          style={styles.newsImageOverlay}
        />
        <Text style={styles.newsImageTitle}>{item.title}</Text>
      </View>

      <View style={styles.newsContent}>
        <View style={styles.newsHeader}>
          <View style={styles.newsMeta}>
            <Text style={styles.newsAuthor}>{item.author}</Text>
            <Text style={styles.newsTime}>{item.publishTime}</Text>
          </View>
          <TouchableOpacity
            style={styles.bookmarkButton}
            onPress={() => toggleBookmark(item.id)}>
            <Icon
              name={item.isBookmarked ? 'bookmark' : 'bookmark-border'}
              size={22}
              color={item.isBookmarked ? '#2E7D32' : '#666'}
            />
          </TouchableOpacity>
        </View>

        <Text style={styles.newsSummary}>{item.summary}</Text>

        <View style={styles.newsTags}>
          {item.tags.map((tag, tagIndex) => (
            <View key={tagIndex} style={styles.newsTag}>
              <Text style={styles.newsTagText}>{tag}</Text>
            </View>
          ))}
        </View>

        <View style={styles.newsFooter}>
          <View style={styles.newsStats}>
            <View style={styles.newsStat}>
              <Icon name="favorite" size={16} color="#F44336" />
              <Text style={styles.newsStatText}>{item.likes}</Text>
            </View>
            <View style={styles.newsStat}>
              <Icon name="comment" size={16} color="#2196F3" />
              <Text style={styles.newsStatText}>{item.comments}</Text>
            </View>
            <Text style={styles.readTime}>{item.readTime}</Text>
          </View>
          <TouchableOpacity style={styles.readMoreButton}>
            <Text style={styles.readMoreText}>Read More</Text>
            <Icon name="arrow-forward" size={16} color="#2E7D32" />
          </TouchableOpacity>
        </View>
      </View>
    </Animatable.View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <LinearGradient colors={['#E8F5E8', '#F0F8F0']} style={styles.gradient}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Travel News</Text>
          <Text style={styles.headerSubtitle}>
            Stay updated with the latest travel information
          </Text>
        </View>

        {renderCategoryFilter()}

        <ScrollView
          style={styles.content}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }>
          {filteredNews.map((item, index) => renderNewsCard(item, index))}
        </ScrollView>
      </LinearGradient>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1 },
  gradient: { flex: 1 },
  header: {
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  headerTitle: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  headerSubtitle: {
    fontSize: 15,
    color: '#666',
    marginTop: 4,
  },

  // Compact category layout
  categoryContainer: {
    marginBottom: 15,
  },
  categoryContent: {
    paddingHorizontal: 12,
    alignItems: 'center',
  },
  categoryButtonNew: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 25,
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: '#fff',
    marginRight: 8,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  categoryButtonNewActive: {
    backgroundColor: '#2E7D32',
    borderColor: '#2E7D32',
    elevation: 4,
  },
  categoryTextNew: {
    fontSize: 14,
    marginLeft: 6,
    color: '#2E7D32',
    fontWeight: '600',
  },
  categoryTextNewActive: {
    color: '#fff',
  },

  content: { flex: 1, paddingHorizontal: 16 },
  newsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 15,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 6,
    overflow: 'hidden',
  },
  newsImageContainer: {
    position: 'relative',
    height: 190,
  },
  newsImage: {
    width: '100%',
    height: '100%',
  },
  newsImageOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 70,
  },
  newsImageTitle: {
    position: 'absolute',
    bottom: 10,
    left: 15,
    right: 15,
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    lineHeight: 24,
  },
  newsContent: { padding: 12 },
  newsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  newsMeta: { flex: 1 },
  newsAuthor: { fontSize: 13, fontWeight: '600', color: '#2E7D32' },
  newsTime: { fontSize: 11, color: '#999', marginTop: 2 },
  bookmarkButton: { padding: 4 },
  newsSummary: {
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
    marginBottom: 10,
  },
  newsTags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
  },
  newsTag: {
    backgroundColor: '#E8F5E8',
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 3,
    marginRight: 5,
    marginBottom: 5,
  },
  newsTagText: {
    fontSize: 11,
    color: '#2E7D32',
    fontWeight: '500',
  },
  newsFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  newsStats: { flexDirection: 'row', alignItems: 'center' },
  newsStat: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 10,
  },
  newsStatText: { fontSize: 13, color: '#666', marginLeft: 3 },
  readTime: { fontSize: 12, color: '#999' },
  readMoreButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E8F5E8',
    borderRadius: 14,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  readMoreText: {
    fontSize: 13,
    color: '#2E7D32',
    fontWeight: '600',
    marginRight: 4,
  },
});

export default TravelNewsScreen;
