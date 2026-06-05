import { useState, useEffect } from 'react';
import styles from '../styles/css/PreTradeCheck.module.css';
import { MessageProperties } from '../services/message';
import api from '../services/api';

interface RiskCalculation {
  risk_per_share: number | null;
  total_risk: number | null;
  risk_percent: number | null;
  trade_value: number | null;
  estimated_pnl_amount: number | null;
  estimated_pnl_percent: number | null;
}

interface RuleViolation {
  rule_type: string;
  message: string;
  severity: string;
  penalty: number;
}

interface EmotionScores {
  fomo_score: number;
  panic_score: number;
  revenge_score: number;
  overconfidence_score: number;
  greed_score: number;
  hesitation_score: number;
}

interface AIIntervention {
  is_required: boolean;
  reflection_question: string;
}

interface TradeCheckResponse {
  log_id: string;
  discipline_score: number;
  discipline_risk: string;
  should_cooldown: boolean;
  coach_message: string;
  emotion_tags: string[];
  risk_calculation: RiskCalculation;
  rule_violations: RuleViolation[];
  emotion_scores: EmotionScores;
  intervention: AIIntervention | null;
}

export default function PreTradeCheck() {
  // Form state
  const [symbol, setSymbol] = useState('');
  const [action, setAction] = useState<'BUY' | 'SELL_TO_CLOSE'>('BUY');
  const [entryPrice, setEntryPrice] = useState('');
  const [sellPrice, setSellPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');
  const [averageEntryPrice, setAverageEntryPrice] = useState('');
  const [reason, setReason] = useState('');
  const [emotionText, setEmotionText] = useState('');
  const [confidenceLevel, setConfidenceLevel] = useState(7);
  const [sessionScore, setSessionScore] = useState(92);

  // Quick tag selection helper
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const emotionTags = ["Calm", "FOMO", "Determined", "Frustrated"];

  // UI Flow state
  const [isLoading, setIsLoading] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const [errorText, setErrorText] = useState<string | null>(null);
  const [tradeResponse, setTradeResponse] = useState<TradeCheckResponse | null>(null);
  const [cooldownMode, setCooldownMode] = useState(false);
  const [reflectiveAnswer, setReflectiveAnswer] = useState('');
  const [isAcknowledgeLoading, setIsAcknowledgeLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Client-side Risk/Reward ratio calculation
  const [clientRR, setClientRR] = useState<string>('—');

  useEffect(() => {
    if (action === 'BUY' && entryPrice && stopLoss && takeProfit) {
      const entry = parseFloat(entryPrice);
      const sl = parseFloat(stopLoss);
      const tp = parseFloat(takeProfit);

      if (entry > 0 && sl > 0 && tp > 0 && entry > sl && tp > entry) {
        const risk = entry - sl;
        const reward = tp - entry;
        const ratio = (reward / risk).toFixed(1);
        setClientRR(`1:${ratio}`);
      } else {
        setClientRR('—');
      }
    } else {
      setClientRR('—');
    }
  }, [action, entryPrice, stopLoss, takeProfit]);

  // Handle Quick tag toggle
  const toggleTag = (tag: string) => {
    let nextTags = [...selectedTags];
    if (selectedTags.includes(tag)) {
      nextTags = nextTags.filter(t => t !== tag);
    } else {
      nextTags.push(tag);
    }
    setSelectedTags(nextTags);

    // Prefill emotionText based on tags
    const vnTagTranslations: Record<string, string> = {
      Calm: "Tôi đang cảm thấy bình tĩnh, tự tin và tuân thủ kỷ luật.",
      FOMO: "Tôi lo sợ cơ hội này sẽ chạy mất nếu không vào lệnh ngay.",
      Determined: "Tôi quyết tâm thực hiện giao dịch này theo đúng chiến lược.",
      Frustrated: "Tôi đang cảm thấy một chút bực bội sau giao dịch trước đó."
    };

    const combinedTexts = nextTags.map(t => vnTagTranslations[t] || t).join(" ");
    setEmotionText(combinedTexts);
  };

  // Submit check trade configuration
  const handleAnalyze = async () => {
    setErrorText(null);

    // Basic frontend validations
    if (!symbol.trim()) {
      setErrorText("Mã chứng khoán không được rỗng");
      return;
    }
    if (!quantity || parseInt(quantity) <= 0) {
      setErrorText("Số lượng phải là số nguyên dương");
      return;
    }

    if (action === 'BUY') {
      if (!entryPrice || parseFloat(entryPrice) <= 0) {
        setErrorText("Giá vào lệnh phải là số dương đối với lệnh BUY");
        return;
      }
      if (stopLoss && parseFloat(stopLoss) >= parseFloat(entryPrice)) {
        setErrorText("Giá Stop-loss phải nhỏ hơn giá vào lệnh (Entry Price)");
        return;
      }
    } else {
      if (!sellPrice || parseFloat(sellPrice) <= 0) {
        setErrorText("Giá bán phải là số dương đối với lệnh SELL_TO_CLOSE");
        return;
      }
    }

    if (!reason.trim()) {
      setErrorText("Vui lòng điền lý do vào lệnh giao dịch");
      return;
    }
    if (!emotionText.trim()) {
      setErrorText("Vui lòng mô tả trạng thái tâm lý cảm xúc hiện tại");
      return;
    }

    try {
      setIsLoading(true);
      setShowOverlay(true);
      setCooldownMode(false);
      setTradeResponse(null);

      const payload = {
        symbol: symbol.trim().toUpperCase(),
        action,
        entry_price: action === 'BUY' ? parseFloat(entryPrice) : null,
        sell_price: action === 'SELL_TO_CLOSE' ? parseFloat(sellPrice) : null,
        quantity: parseInt(quantity),
        stop_loss: action === 'BUY' && stopLoss ? parseFloat(stopLoss) : null,
        take_profit: action === 'BUY' && takeProfit ? parseFloat(takeProfit) : null,
        average_entry_price: action === 'SELL_TO_CLOSE' && averageEntryPrice ? parseFloat(averageEntryPrice) : null,
        reason: reason.trim(),
        emotion_text: emotionText.trim(),
        confidence_level: confidenceLevel
      };

      const res = await api.post<TradeCheckResponse>('/trade-check', payload);
      setTradeResponse(res.data);
      setSessionScore(res.data.discipline_score);

      if (res.data.should_cooldown) {
        setCooldownMode(true);
      }
    } catch (err: any) {
      console.error(err);
      setErrorText(
        err.response?.data?.detail || 
        MessageProperties.CONNECTION_FAILED
      );
      setShowOverlay(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Submit cooldown acknowledgment
  const handleAcknowledge = async () => {
    if (!tradeResponse || reflectiveAnswer.trim().length < 10) return;

    try {
      setIsAcknowledgeLoading(true);
      await api.post(`/trade-check/${tradeResponse.log_id}/acknowledge`, {
        reflective_answer: reflectiveAnswer.trim()
      });

      // Acknowledged successfully, turn off cooldown view to display final results
      setCooldownMode(false);
      setToastMessage("Đã ghi nhận phản tỉnh. Kỷ luật giao dịch được cập nhật.");
      setTimeout(() => setToastMessage(null), 4000);
    } catch (err: any) {
      console.error(err);
      setErrorText(err.response?.data?.detail || "Không thể lưu câu trả lời phản tỉnh.");
    } finally {
      setIsAcknowledgeLoading(false);
    }
  };

  const handleReset = () => {
    setShowOverlay(false);
    setTradeResponse(null);
    setCooldownMode(false);
    setReflectiveAnswer('');
  };

  const handleConfirmSave = () => {
    // Confirm and save to journal (mocked behavior for MVP)
    setToastMessage("Giao dịch đã được lưu nháp vào nhật ký (Journal)!");
    setTimeout(() => setToastMessage(null), 4000);
    setShowOverlay(false);
    // Clear form inputs
    setSymbol('');
    setEntryPrice('');
    setSellPrice('');
    setQuantity('');
    setStopLoss('');
    setTakeProfit('');
    setAverageEntryPrice('');
    setReason('');
    setEmotionText('');
    setSelectedTags([]);
  };

  return (
    <div className={styles.wrapper}>
      {/* Toast message notification */}
      {toastMessage && (
        <div className={`${styles.toast} ${styles.showToast}`}>
          <span className="material-symbols-outlined">verified_user</span>
          <div className={styles.toastText}>
            <span className={styles.toastTitle}>Đồng bộ hóa thành công</span>
            <span className={styles.toastDesc}>{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Header section */}
      <section className={styles.headerSection}>
        <div>
          <h2 className={styles.headerTitle}>{MessageProperties.PRETRADE_PAGE_TITLE}</h2>
          <p className={styles.headerDesc}>{MessageProperties.PRETRADE_PAGE_DESC}</p>
        </div>
        <div className={styles.scoreWrapper}>
          <div className={styles.scoreLabel}>{MessageProperties.PRETRADE_DISCIPLINE_SCORE_LABEL}</div>
          <div className={styles.scoreVal}>{sessionScore}</div>
        </div>
      </section>

      {errorText && (
        <div className={styles.errorBanner}>
          <strong>Lỗi: </strong> {errorText}
        </div>
      )}

      {/* Bento Grid layout */}
      <form className={styles.bentoGrid} onSubmit={(e) => e.preventDefault()}>
        {/* Left column */}
        <div className={styles.column}>
          {/* Trade Configuration */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={`material-symbols-outlined ${styles.cardIcon}`}>analytics</span>
              <h3 className={styles.cardTitle}>{MessageProperties.PRETRADE_CARD_CONFIG_TITLE}</h3>
            </div>
            
            <div className={styles.grid2Col}>
              <div className={styles.formGroup}>
                <label className={styles.label}>{MessageProperties.PRETRADE_SYMBOL_LABEL}</label>
                <input
                  type="text"
                  className={`${styles.input} ${styles.inputMono}`}
                  placeholder={MessageProperties.PRETRADE_SYMBOL_PLACEHOLDER}
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                />
              </div>

              <div className={styles.formGroup}>
                <label className={styles.label}>{MessageProperties.PRETRADE_ACTION_LABEL}</label>
                <div className={styles.actionToggle}>
                  <button
                    type="button"
                    className={`${styles.toggleBtn} ${action === 'BUY' ? styles.btnBuyActive : ''}`}
                    onClick={() => setAction('BUY')}
                  >
                    {MessageProperties.PRETRADE_ACTION_BUY}
                  </button>
                  <button
                    type="button"
                    className={`${styles.toggleBtn} ${action === 'SELL_TO_CLOSE' ? styles.btnSellActive : ''}`}
                    onClick={() => setAction('SELL_TO_CLOSE')}
                  >
                    {MessageProperties.PRETRADE_ACTION_SELL}
                  </button>
                </div>
              </div>

              {action === 'BUY' ? (
                <div className={styles.formGroup}>
                  <label className={styles.label}>{MessageProperties.PRETRADE_ENTRY_PRICE_LABEL}</label>
                  <div className={styles.inputWrapper}>
                    <span className={styles.inputPrefix}>$</span>
                    <input
                      type="number"
                      step="any"
                      className={`${styles.input} ${styles.inputMono} ${styles.inputWithPrefix}`}
                      placeholder={MessageProperties.PRETRADE_PRICE_PLACEHOLDER}
                      value={entryPrice}
                      onChange={(e) => setEntryPrice(e.target.value)}
                    />
                  </div>
                </div>
              ) : (
                <div className={styles.formGroup}>
                  <label className={styles.label}>{MessageProperties.PRETRADE_SELL_PRICE_LABEL}</label>
                  <div className={styles.inputWrapper}>
                    <span className={styles.inputPrefix}>$</span>
                    <input
                      type="number"
                      step="any"
                      className={`${styles.input} ${styles.inputMono} ${styles.inputWithPrefix}`}
                      placeholder={MessageProperties.PRETRADE_PRICE_PLACEHOLDER}
                      value={sellPrice}
                      onChange={(e) => setSellPrice(e.target.value)}
                    />
                  </div>
                </div>
              )}

              <div className={styles.formGroup}>
                <label className={styles.label}>{MessageProperties.PRETRADE_QUANTITY_LABEL}</label>
                <input
                  type="number"
                  className={`${styles.input} ${styles.inputMono}`}
                  placeholder={MessageProperties.PRETRADE_QUANTITY_PLACEHOLDER}
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                />
              </div>

              {action === 'SELL_TO_CLOSE' && (
                <div className={styles.formGroup}>
                  <label className={styles.label}>Average Entry Price</label>
                  <div className={styles.inputWrapper}>
                    <span className={styles.inputPrefix}>$</span>
                    <input
                      type="number"
                      step="any"
                      className={`${styles.input} ${styles.inputMono} ${styles.inputWithPrefix}`}
                      placeholder="0.00"
                      value={averageEntryPrice}
                      onChange={(e) => setAverageEntryPrice(e.target.value)}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Strategic Rationale */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={`material-symbols-outlined ${styles.cardIcon}`}>psychology</span>
              <h3 className={styles.cardTitle}>{MessageProperties.PRETRADE_RATIONALE_TITLE}</h3>
            </div>
            
            <div className={styles.formGroup} style={{ marginBottom: '24px' }}>
              <label className={styles.label}>{MessageProperties.PRETRADE_REASON_LABEL}</label>
              <textarea
                rows={4}
                className={styles.textarea}
                placeholder={MessageProperties.PRETRADE_REASON_PLACEHOLDER}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
              />
            </div>

            <div className={styles.formGroup}>
              <div className={styles.convictionHeader}>
                <label className={styles.label}>{MessageProperties.PRETRADE_CONVICTION_LABEL}</label>
                <span className={styles.convictionVal}>{confidenceLevel} / 10</span>
              </div>
              <input
                type="range"
                min={0}
                max={10}
                className={styles.slider}
                value={confidenceLevel}
                onChange={(e) => setConfidenceLevel(parseInt(e.target.value))}
              />
              <div className={styles.sliderLabels}>
                <span>{MessageProperties.PRETRADE_CONVICTION_SPECULATIVE}</span>
                <span>{MessageProperties.PRETRADE_CONVICTION_HIGH}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right column */}
        <div className={styles.column}>
          {/* Risk Guardrails */}
          <div className={styles.card} style={{ borderLeft: '4px solid hsl(var(--color-danger))' }}>
            <div className={styles.cardHeader}>
              <span className="material-symbols-outlined" style={{ color: 'hsl(var(--color-danger))', fontSize: '24px' }}>security</span>
              <h3 className={styles.cardTitle}>{MessageProperties.PRETRADE_GUARDRAILS_TITLE}</h3>
            </div>

            <div className={styles.formGroup} style={{ marginBottom: '20px' }}>
              <label className={styles.label}>{MessageProperties.PRETRADE_STOP_LOSS_LABEL}</label>
              <input
                type="number"
                step="any"
                disabled={action === 'SELL_TO_CLOSE'}
                className={`${styles.input} ${styles.inputMono}`}
                placeholder={action === 'SELL_TO_CLOSE' ? "DISABLED" : MessageProperties.PRETRADE_STOP_LOSS_PLACEHOLDER}
                value={action === 'SELL_TO_CLOSE' ? '' : stopLoss}
                onChange={(e) => setStopLoss(e.target.value)}
              />
              {action === 'BUY' && !stopLoss && (
                <p className={styles.warningText}>
                  <span className={`material-symbols-outlined ${styles.warningIcon}`}>warning</span>
                  {MessageProperties.PRETRADE_STOP_LOSS_WARNING}
                </p>
              )}
            </div>

            <div className={styles.formGroup} style={{ marginBottom: '24px' }}>
              <label className={styles.label}>{MessageProperties.PRETRADE_TAKE_PROFIT_LABEL}</label>
              <input
                type="number"
                step="any"
                disabled={action === 'SELL_TO_CLOSE'}
                className={`${styles.input} ${styles.inputMono}`}
                placeholder={action === 'SELL_TO_CLOSE' ? "DISABLED" : MessageProperties.PRETRADE_TAKE_PROFIT_PLACEHOLDER}
                value={action === 'SELL_TO_CLOSE' ? '' : takeProfit}
                onChange={(e) => setTakeProfit(e.target.value)}
              />
            </div>

            <div className={styles.riskRewardContainer}>
              <span className={styles.label} style={{ marginBottom: 0 }}>{MessageProperties.PRETRADE_RISK_REWARD_LABEL}</span>
              <span className={`${styles.rrVal} ${clientRR !== '—' ? 'text-emerald-500' : 'text-slate-500'}`} style={{ color: clientRR !== '—' ? 'hsl(var(--color-success))' : 'hsl(var(--text-muted))' }}>
                {clientRR}
              </span>
            </div>
          </div>

          {/* Mental State */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <span className={`material-symbols-outlined ${styles.cardIcon}`}>face</span>
              <h3 className={styles.cardTitle}>{MessageProperties.PRETRADE_MENTAL_STATE_TITLE}</h3>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>{MessageProperties.PRETRADE_MENTAL_STATE_LABEL}</label>
              <textarea
                rows={6}
                className={styles.textarea}
                placeholder={MessageProperties.PRETRADE_MENTAL_STATE_PLACEHOLDER}
                value={emotionText}
                onChange={(e) => setEmotionText(e.target.value)}
              />
            </div>

            <div className={styles.quickTags}>
              {emotionTags.map(tag => (
                <span
                  key={tag}
                  className={`${styles.tag} ${selectedTags.includes(tag) ? styles.tagActive : ''}`}
                  onClick={() => toggleTag(tag)}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Disclaimer Vietnamese */}
        <div className="col-span-12">
          <p className={styles.disclaimerBanner}>
            * {MessageProperties.PRETRADE_DISCLAIMER_VN}
          </p>
        </div>

        {/* Sticky CTA Bar */}
        <div className="col-span-12" style={{ width: '100%' }}>
          <div className={styles.footerBar}>
            <div className={styles.footerLeft}>
              <div className={styles.footerStatusIcon}>
                <span className="material-symbols-outlined">verified_user</span>
              </div>
              <p className={styles.footerText}>{MessageProperties.PRETRADE_FOOTER_MESSAGE}</p>
            </div>
            <div className={styles.footerRight}>
              <button
                type="button"
                className={styles.btnDraft}
                onClick={handleConfirmSave}
              >
                {MessageProperties.PRETRADE_BTN_DRAFT}
              </button>
              <button
                type="button"
                className={styles.btnAnalyze}
                onClick={handleAnalyze}
              >
                {MessageProperties.PRETRADE_BTN_ANALYZE}
              </button>
            </div>
          </div>
        </div>
      </form>

      {/* Analysis and Cooldown Overlay */}
      {showOverlay && (
        <div className={styles.overlay}>
          <div className={styles.overlayCard}>
            {/* 1. Loading State */}
            {isLoading && (
              <div>
                <div className={styles.loaderSpinner}></div>
                <h3 className={styles.loaderTitle}>{MessageProperties.PRETRADE_LOADING_TITLE}</h3>
                <p className={styles.loaderDesc}>{MessageProperties.PRETRADE_LOADING_DESC}</p>
              </div>
            )}

            {/* 2. Cooldown Intervention Modal */}
            {!isLoading && cooldownMode && tradeResponse && (
              <div className={styles.cooldownContainer}>
                <span className={`material-symbols-outlined ${styles.cooldownIcon}`}>warning</span>
                <h3 className={styles.cooldownTitle}>{MessageProperties.PRETRADE_COOLDOWN_TITLE}</h3>
                
                <div className={styles.cooldownBox}>
                  <p className={styles.label}>{MessageProperties.PRETRADE_COOLDOWN_DIAGNOSIS_LABEL}</p>
                  <p className={styles.cooldownDiagnosis}>
                    "{tradeResponse.coach_message}"
                  </p>

                  <p className={`${styles.label} ${styles.reflectionLabel}`}>
                    {MessageProperties.PRETRADE_COOLDOWN_REFLECTION_LABEL}
                  </p>
                  <p style={{ fontSize: '0.8125rem', color: 'hsl(var(--text-secondary))', marginBottom: '8px' }}>
                    {tradeResponse.intervention?.reflection_question}
                  </p>
                  <textarea
                    rows={4}
                    className={styles.cooldownTextarea}
                    placeholder={MessageProperties.PRETRADE_COOLDOWN_REFLECTION_PLACEHOLDER}
                    value={reflectiveAnswer}
                    onChange={(e) => setReflectiveAnswer(e.target.value)}
                  />
                  {reflectiveAnswer.trim().length < 10 && (
                    <p style={{ color: 'hsl(var(--color-warning))', fontSize: '0.75rem', marginTop: '6px' }}>
                      (Nhập tối thiểu 10 ký tự để xác nhận. Hiện tại: {reflectiveAnswer.trim().length} ký tự)
                    </p>
                  )}
                </div>

                <div className={styles.cooldownActions}>
                  <button
                    type="button"
                    className={styles.cooldownCancel}
                    onClick={handleReset}
                  >
                    {MessageProperties.PRETRADE_COOLDOWN_BTN_CANCEL}
                  </button>
                  <button
                    type="button"
                    disabled={reflectiveAnswer.trim().length < 10 || isAcknowledgeLoading}
                    className={styles.cooldownProceed}
                    onClick={handleAcknowledge}
                  >
                    {isAcknowledgeLoading ? "Acknowledging..." : MessageProperties.PRETRADE_COOLDOWN_BTN_PROCEED}
                  </button>
                </div>
              </div>
            )}

            {/* 3. Normal Analysis Result Summary */}
            {!isLoading && !cooldownMode && tradeResponse && (
              <div className={styles.resultContainer}>
                <div className={styles.resultHeader}>
                  <div className={`
                    ${styles.resultScoreCircle}
                    ${tradeResponse.discipline_risk === 'Medium' ? styles.resultScoreCircleWarning : ''}
                    ${tradeResponse.discipline_risk === 'High' ? styles.resultScoreCircleDanger : ''}
                  `}>
                    <span className={`
                      ${styles.resultScoreText}
                      ${tradeResponse.discipline_risk === 'Low' ? 'text-emerald-500' : ''}
                      ${tradeResponse.discipline_risk === 'Medium' ? 'text-amber-500' : ''}
                      ${tradeResponse.discipline_risk === 'High' ? 'text-rose-500' : ''}
                    `}>
                      {tradeResponse.discipline_score}
                    </span>
                  </div>
                  <h3 className={styles.resultTitle}>
                    Behavioral Analysis: {tradeResponse.discipline_risk} Risk
                  </h3>
                </div>

                <div className={styles.resultBox}>
                  <p className={styles.label}>Huấn luyện viên AI khuyên:</p>
                  <p className={styles.resultDiagnosis}>
                    {tradeResponse.coach_message}
                  </p>

                  {tradeResponse.rule_violations.length > 0 ? (
                    <>
                      <p className={styles.resultViolationsTitle}>Vi phạm kỷ luật phát hiện:</p>
                      <div className={styles.resultViolationsList}>
                        {tradeResponse.rule_violations.map((v, i) => (
                          <div key={i} className={styles.resultViolationItem}>
                            <span className={styles.violationMsg}>{v.message}</span>
                            <span className={`
                              ${styles.violationSeverity}
                              ${v.severity === 'high' ? styles.severityHigh : ''}
                              ${v.severity === 'critical' ? styles.severityCritical : ''}
                              ${v.severity === 'medium' ? styles.severityMedium : ''}
                              ${v.severity === 'low' ? styles.severityLow : ''}
                            `}>
                              {v.severity} ({v.penalty})
                            </span>
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <p style={{ color: 'hsl(var(--color-success))', fontSize: '0.8125rem', fontWeight: 600 }}>
                      ✓ Không phát hiện vi phạm quy tắc kỷ luật nào.
                    </p>
                  )}
                </div>

                <div className={styles.resultActions}>
                  <button
                    type="button"
                    className={styles.resultClose}
                    onClick={handleReset}
                  >
                    Edit Trade
                  </button>
                  <button
                    type="button"
                    className={styles.resultConfirm}
                    onClick={handleConfirmSave}
                  >
                    Save to Journal
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
