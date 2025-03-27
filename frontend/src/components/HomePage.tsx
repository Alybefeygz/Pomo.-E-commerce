import React from 'react';
import { Layout, Typography, Button, Card, Row, Col, Space, Divider } from 'antd';
import {
  CalculatorOutlined,
  LineChartOutlined,
  DatabaseOutlined,
  ShopOutlined,
  BarChartOutlined,
  CheckCircleOutlined,
  UserOutlined,
  RocketOutlined,
  StarOutlined,
  BookOutlined,
} from '@ant-design/icons';

const { Header, Content, Footer } = Layout;
const { Title, Paragraph } = Typography;

// Define empty handler functions for pointer events
const emptyPointerHandler = () => {};

const HomePage: React.FC = () => {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    element?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <Layout className="homepage-layout">
      {/* Hero Section */}
      <section id="hero" className="hero-section">
        <div className="hero-content">
          <div className="hero-text">
            <Title level={1}>E-Ticaretinizi Akıllıca Yönetin</Title>
            <Paragraph className="hero-subtitle">
              Ücretsiz hesaplama araçları ve yapay zeka destekli çözümlerle e-ticaretinizi büyütün.
            </Paragraph>
            <Space size="large">
              <Button type="primary" size="large" icon={<CalculatorOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />}>
                Ücretsiz Hesaplama Yap
              </Button>
              <Button size="large" icon={<RocketOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />}>
                Demo İste
              </Button>
            </Space>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <Title level={2} className="section-title">Hizmetler ve Öne Çıkan Özellikler</Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} sm={12} md={8}>
            <Card className="feature-card">
              <CalculatorOutlined className="feature-icon" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
              <Title level={4}>Ücretsiz Hesaplamalar</Title>
              <Paragraph>Fiyat, komisyon, kargo maliyeti hesaplama</Paragraph>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card className="feature-card">
              <LineChartOutlined className="feature-icon" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
              <Title level={4}>Rakip Analizi</Title>
              <Paragraph>Yapay zeka destekli rakip takibi</Paragraph>
            </Card>
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Card className="feature-card">
              <DatabaseOutlined className="feature-icon" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
              <Title level={4}>Stok Takip Sistemi</Title>
              <Paragraph>Gelişmiş stok yönetimi</Paragraph>
            </Card>
          </Col>
        </Row>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="how-it-works-section">
        <Title level={2} className="section-title">3 Adımda Pomo.e-commerce</Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card className="step-card">
              <div className="step-number">1</div>
              <UserOutlined className="step-icon" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
              <Title level={4}>Kaydol / Giriş Yap</Title>
              <Paragraph>Hızlı ve güvenli hesap oluşturma</Paragraph>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="step-card">
              <div className="step-number">2</div>
              <ShopOutlined className="step-icon" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
              <Title level={4}>İhtiyacını Seç</Title>
              <Paragraph>Ücretsiz araçlar veya premium abonelik</Paragraph>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="step-card">
              <div className="step-number">3</div>
              <RocketOutlined className="step-icon" onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
              <Title level={4}>E-Ticaretini Büyüt</Title>
              <Paragraph>Akıllı araçlarla işini büyüt</Paragraph>
            </Card>
          </Col>
        </Row>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="pricing-section">
        <Title level={2} className="section-title">Fiyatlandırma</Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card className="pricing-card">
              <Title level={3}>Ücretsiz</Title>
              <div className="price">₺0/ay</div>
              <ul className="features-list">
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> Temel Hesaplamalar</li>
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> E-posta Destek</li>
              </ul>
              <Button type="primary" block>Başla</Button>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="pricing-card featured">
              <Title level={3}>Pro</Title>
              <div className="price">₺9/ay</div>
              <ul className="features-list">
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> Temel Hesaplamalar</li>
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> 5 Rakip Analizi</li>
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> 100 Ürün Stok Takibi</li>
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> Canlı Destek</li>
              </ul>
              <Button type="primary" block>14 Gün Ücretsiz Dene</Button>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="pricing-card">
              <Title level={3}>Business</Title>
              <div className="price">₺29/ay</div>
              <ul className="features-list">
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> Tüm Özellikler</li>
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> Sınırsız Rakip Analizi</li>
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> Sınırsız Stok Takibi</li>
                <li><CheckCircleOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} /> VIP Destek</li>
              </ul>
              <Button type="primary" block>14 Gün Ücretsiz Dene</Button>
            </Card>
          </Col>
        </Row>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="testimonials-section">
        <Title level={2} className="section-title">Müşteri Yorumları</Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={12}>
            <Card className="testimonial-card">
              <Space direction="vertical">
                <div className="rating">
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                </div>
                <Paragraph>"Pomo ile aylık kârım %30 arttı!"</Paragraph>
                <Paragraph strong>- Ahmet Y., Shopify Mağaza Sahibi</Paragraph>
              </Space>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card className="testimonial-card">
              <Space direction="vertical">
                <div className="rating">
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                  <StarOutlined onPointerEnterCapture={emptyPointerHandler} onPointerLeaveCapture={emptyPointerHandler} />
                </div>
                <Paragraph>"Rakip analizi özelliği mükemmel!"</Paragraph>
                <Paragraph strong>- Ayşe K., E-ticaret Danışmanı</Paragraph>
              </Space>
            </Card>
          </Col>
        </Row>
      </section>

      {/* Blog Section */}
      <section id="blog" className="blog-section">
        <Title level={2} className="section-title">Blog / E-Ticaret İpuçları</Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={8}>
            <Card className="blog-card" cover={<div className="blog-image" />}>
              <Title level={4}>E-ticarette Kâr Marjı Nasıl Artırılır?</Title>
              <Button type="link">Devamını Oku</Button>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="blog-card" cover={<div className="blog-image" />}>
              <Title level={4}>2024'te En Çok Satan Ürünler</Title>
              <Button type="link">Devamını Oku</Button>
            </Card>
          </Col>
          <Col xs={24} md={8}>
            <Card className="blog-card" cover={<div className="blog-image" />}>
              <Title level={4}>Pazaryeri Entegrasyon Rehberi</Title>
              <Button type="link">Devamını Oku</Button>
            </Card>
          </Col>
        </Row>
      </section>

      {/* Footer */}
      <Footer className="homepage-footer">
        <Row gutter={[24, 24]}>
          <Col xs={24} md={6}>
            <Title level={4}>Hızlı Linkler</Title>
            <ul className="footer-links">
              <li><a href="#hero">Anasayfa</a></li>
              <li><a href="#features">Hizmetler</a></li>
              <li><a href="#pricing">Fiyatlar</a></li>
              <li><a href="#blog">Blog</a></li>
            </ul>
          </Col>
          <Col xs={24} md={6}>
            <Title level={4}>İletişim</Title>
            <ul className="footer-links">
              <li>E-posta: info@pomo.com</li>
              <li>Tel: +90 555 123 4567</li>
            </ul>
          </Col>
          <Col xs={24} md={6}>
            <Title level={4}>Abonelik</Title>
            <Paragraph>E-bültenimize kayıt olun</Paragraph>
            <Button type="primary">Kayıt Ol</Button>
          </Col>
          <Col xs={24} md={6}>
            <Title level={4}>Güvenceler</Title>
            <div className="security-badges">
              <span>SSL</span>
              <span>256-bit</span>
            </div>
          </Col>
        </Row>
        <Divider />
        <div className="footer-bottom">
          <Paragraph>© 2024 Pomo.e-commerce. Tüm hakları saklıdır.</Paragraph>
        </div>
      </Footer>
    </Layout>
  );
};

export default HomePage; 