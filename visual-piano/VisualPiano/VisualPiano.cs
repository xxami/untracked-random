
using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

namespace VisualPiano
{
    #region Enums/Constants

    /// <summary>
    /// Used to determine the animation/visual state of a piano key
    /// </summary>
    public enum PianoKeyStates
    {
        DEFAULT, // Default key state
        HOVER, // Mouse is hovering over key
        ACTIVE, // Key is pressed down
    }

    /// <summary>
    /// Piano key notes in order of key index (left to right)
    /// </summary>
    public enum PianoKeyNotes
    {
        C_1,
        D_1,
        C_1_SHARP,
        E_1,
        D_1_SHARP,
        F_1,
        G_1,
        F_1_SHARP,
        A_1,
        G_1_SHARP,
        B_1,
        A_1_SHARP,
        C_2,
        D_2,
        C_2_SHARP,
        E_2,
        D_2_SHARP,
        F_2,
        G_2,
        F_2_SHARP,
        A_2,
        G_2_SHARP,
        B_2,
        A_2_SHARP,
        C_3,
        D_3,
        C_3_SHARP,
        E_3,
        D_3_SHARP,
        F_3,
        G_3,
        F_3_SHARP,
        A_3,
        G_3_SHARP,
        B_3,
        A_3_SHARP,
        C_4,
        D_4,
        C_4_SHARP,
        E_4,
        D_4_SHARP,
        F_4,
        G_4,
        F_4_SHARP,
        A_4,
        G_4_SHARP,
        B_4,
        A_4_SHARP,
        C_5,
        D_5,
        C_5_SHARP,
        E_5,
        D_5_SHARP,
        F_5,
        G_5,
        F_5_SHARP,
        A_5,
        G_5_SHARP,
        B_5,
        A_5_SHARP,
        C_6,
        D_6,
        C_6_SHARP,
        E_6,
        D_6_SHARP,
        F_6,
        G_6,
        F_6_SHARP,
        A_6,
        G_6_SHARP,
        B_6,
        A_6_SHARP,
        C_7,
        D_7,
        C_7_SHARP,
        E_7,
        D_7_SHARP,
        F_7,
        G_7,
        F_7_SHARP,
        A_7,
        G_7_SHARP,
        B_7,
        A_7_SHARP,
    }

    /// <summary>
    /// Static class containing misc const values
    /// </summary>
    public static class PianoConstants
    {
        /// <summary>
        /// Index/PianoKeyNotes to string lookup
        /// </summary>
        public static readonly string[] STRINGS = new string[]
        {
            "C1",
            "D1",
            "C#1",
            "E1",
            "D#1",
            "F1",
            "G1",
            "F#1",
            "A1",
            "G#1",
            "B1",
            "A#1",
            "C2",
            "D2",
            "C#2",
            "E2",
            "D#2",
            "F2",
            "G2",
            "F#2",
            "A2",
            "G#2",
            "B2",
            "A#2",
            "C3",
            "D3",
            "C#3",
            "E3",
            "D#3",
            "F3",
            "G3",
            "F#3",
            "A3",
            "G#3",
            "B3",
            "A#3",
            "C4",
            "D4",
            "C#4",
            "E4",
            "D#4",
            "F4",
            "G4",
            "F#4",
            "A4",
            "G#4",
            "B4",
            "A#4",
            "C5",
            "D5",
            "C#5",
            "E5",
            "D#5",
            "F5",
            "G5",
            "F#5",
            "A5",
            "G#5",
            "B5",
            "A#5",
            "C6",
            "D6",
            "C#6",
            "E6",
            "D#6",
            "F6",
            "G6",
            "F#6",
            "A6",
            "G#6",
            "B6",
            "A#6",
            "C7",
            "D7",
            "C#7",
            "E7",
            "D#7",
            "F7",
            "G7",
            "F#7",
            "A7",
            "G#7",
            "B7",
            "A#7",
        };

        /// <summary>
        /// Index/PianoKeyNotes to frequency lookup
        /// </summary>
        public static readonly float[] FREQUENCIES = new float[]
        {
            32.7f,
            36.7f,
            34.6f,
            41.2f,
            38.8f,
            43.7f,
            49.0f,
            46.2f,
            55.0f,
            51.9f,
            61.7f,
            58.2f,
            65.4f,
            73.4f,
            69.2f,
            82.4f,
            77.7f,
            87.3f,
            98.0f,
            92.4f,
            110.0f,
            103.8f,
            123.5f,
            116.5f,
            130.8f,
            146.8f,
            137.7f,
            164.8f,
            155.5f,
            174.6f,
            196.0f,
            184.9f,
            220.0f,
            207.6f,
            246.9f,
            233.0f,
            261.6f,
            293.7f,
            277.1f,
            329.6f,
            311.1f,
            349.2f,
            392.0f,
            369.9f,
            440.0f,
            415.3f,
            493.9f,
            466.1f,
            523.3f,
            587.3f,
            554.4f,
            659.3f,
            622.2f,
            698.5f,
            784.0f,
            740.0f,
            880.0f,
            830.6f,
            987.8f,
            932.3f,
            1046.5f,
            1174.7f,
            1108.7f,
            1318.5f,
            1244.5f,
            1396.9f,
            1568.0f,
            1479.9f,
            1760.0f,
            1661.2f,
            1979.5f,
            1864.6f,
            2093.0f,
            2349.3f,
            2217.4f,
            2637.0f,
            2488.9f,
            2793.8f,
            3136.0f,
            2959.9f,
            3520.0f,
            3322.4f,
            3951.1f,
            3729.3f,
        };

        /// <summary>
        /// Octave constants
        /// </summary>
        public const int OCTAVE_FIRST = 1;
        public const int OCTAVE_SECOND = 2;
        public const int OCTAVE_THIRD = 3;
        public const int OCTAVE_FOURTH = 4;
        public const int OCTAVE_FIFTH = 5;
        public const int OCTAVE_SIXTH = 6;
        public const int OCTAVE_SEVENTH = 7;

        /// <summary>
        /// Octave bounds constants
        /// </summary>
        public const int OCTAVES_MIN = 1;
        public const int OCTAVES_MAX = 7;

        /// <summary>
        /// Key constants
        /// </summary>
        public const int KEYS_PER_OCTAVE = 12;
    }

    #endregion

    #region Custom Types

    /// <summary>
    /// Paino key data type
    /// </summary>
    public struct PianoKey
    {
        // nth-1 key index from the left
        public int index;

        // Key note
        public PianoKeyNotes note;
        
        // Key note as string (ie. "C#1")
        public string name;

        // Frequency of note
        public float frequency;

        // Bounding box of the key
        public Rectangle bounds;

        // Current state of the key
        public PianoKeyStates state;

        // Is this a black key?
        public bool is_semitone;
    }

    #endregion

    #region Main/Control-derived Class

    /// <summary>
    /// WinForms Piano control
    /// </summary>
    public partial class VisualPiano : Control
    {
        #region Fields

        // Main piano key colours
        private Color key_color_full_a = Color.White;
        private Color key_color_full_b = Color.LightGray;
        private Color key_color_full_hover = Color.LightBlue;
        private Color key_color_full_active = Color.LightYellow;

        // Semi-tone piano key colours
        private Color key_color_semi_a = Color.Black;
        private Color key_color_semi_b = Color.DimGray;
        private Color key_color_semi_hover = Color.DarkRed;
        private Color key_color_semi_active = Color.LightPink;

        // Piano key dimensions
        private Size key_size = new Size(14, 100);

        // Number of octaves displayed
        private int octave_count = PianoConstants.OCTAVES_MAX;
        
        // AutoSize
        private bool auto_size = true;
        private Size size = Size.Empty;

        // List of keys, this must be populated with InitPianoKeys() when necessary
        private List<PianoKey> key_list = new List<PianoKey>();

        #endregion Fields

        #region Properties

        /// <summary>
        /// Main color for the traditionally white piano keys
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Main color for the traditionally white piano keys.")]
        public Color KeyColorFullA
        {
            get { return this.key_color_full_a; }
            set { this.key_color_full_a = value; this.Invalidate(); }
        }

        /// <summary>
        /// Highlight color for the traditionally white piano keys
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Highlight color for the traditionally white piano keys.")]
        public Color KeyColorFullB
        {
            get { return this.key_color_full_b; }
            set { this.key_color_full_b = value; this.Invalidate(); }
        }

        /// <summary>
        /// Hover color for the traditionally white piano keys
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Hover color for the traditionally white piano keys.")]
        public Color KeyColorFullHover
        {
            get { return this.key_color_full_hover; }
            set { this.key_color_full_hover = value; this.Invalidate(); }
        }

        /// <summary>
        /// Active/pressed color for the traditionally white piano keys
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Active/pressed color for the traditionally white piano keys.")]
        public Color KeyColorFullActive
        {
            get { return this.key_color_full_active; }
            set { this.key_color_full_active = value; this.Invalidate(); }
        }

        /// <summary>
        /// Main color for the traditionally black piano keys
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Main color for the traditionally black piano keys.")]
        public Color KeyColorSemiA
        {
            get { return this.key_color_semi_a; }
            set { this.key_color_semi_a = value; this.Invalidate(); }
        }

        /// <summary>
        /// Highlight color for the traditionally black piano keys
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Highlight color for the traditionally black piano keys.")]
        public Color KeyColorSemiB
        {
            get { return this.key_color_semi_b; }
            set { this.key_color_semi_b = value; this.Invalidate(); }
        }

        /// <summary>
        /// Hover color for the traditionally black piano keys
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Hover color for the traditionally black piano keys.")]
        public Color KeyColorSemiHover
        {
            get { return this.key_color_semi_hover; }
            set { this.key_color_semi_hover = value; this.Invalidate(); }
        }

        /// <summary>
        /// Active/pressed color for the traditionally black piano keys
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Active/pressed color for the traditionally black piano keys.")]
        public Color KeyColorSemiActive
        {
            get { return this.key_color_semi_active; }
            set { this.key_color_semi_active = value; this.Invalidate(); }
        }

        /// <summary>
        /// Size of each individual piano key (min-width: 10, min-height: 32)
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Size of each individual piano key (min-width: 10, min-height: 32)."),
        DefaultValue(typeof(Size), "14, 100")]
        public Size KeySize
        {
            get { return this.key_size; }
            set
            {
                if (value != this.key_size && value.Width >= 10 && value.Height >= 32)
                {
                    this.key_size = value;
                    if (this.auto_size) this.size = this.GetIdealSize();
                    base.SetBoundsCore(this.Location.X, this.Location.Y,
                    this.size.Width, this.size.Height, BoundsSpecified.Size);
                    this.InitPianoKeys();
                    this.Invalidate();
                }
            }
        }

        /// <summary>
        /// Total number of octaves to display (min: 1, max: 7)
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Total number of octaves to display (min: 1, max: 7)."),
        DefaultValue(PianoConstants.OCTAVES_MAX)]
        public int Octaves
        {
            get { return this.octave_count; }
            set
            {
                if (value != this.octave_count && value >= PianoConstants.OCTAVES_MIN && value <= PianoConstants.OCTAVES_MAX)
                {
                    this.octave_count = value;
                    if (this.auto_size) this.size = this.GetIdealSize();
                    base.SetBoundsCore(this.Location.X, this.Location.Y,
                    this.size.Width, this.size.Height, BoundsSpecified.Size);
                    this.InitPianoKeys();
                    this.Invalidate();
                }
            }
        }

        /// <summary>
        /// If true, sizing will scale to fit the controls drawn size
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("If true, sizing will scale to fit the controls drawn size.")]
        public override bool AutoSize
        {
            get { return this.auto_size; }
            set
            {
                this.auto_size = value; 
                if (this.auto_size) this.size = this.GetIdealSize();
                base.SetBoundsCore(this.Location.X, this.Location.Y,
                    this.size.Width, this.size.Height, BoundsSpecified.Size);
                this.Invalidate();
            }
        }

        /// <summary>
        /// Size of the control, read-only if AutoSize is true
        /// </summary>
        [Browsable(true), EditorBrowsable(EditorBrowsableState.Always),
        DesignerSerializationVisibility(DesignerSerializationVisibility.Visible),
        Description("Size of the control, read-only if AutoSize is true")]
        new public Size Size
        {
            get { return this.size; }
            set
            {
                if (this.auto_size) this.size = this.GetIdealSize();
                else this.size = value;
                base.SetBoundsCore(this.Location.X, this.Location.Y,
                    this.size.Width, this.size.Height, BoundsSpecified.Size);
                this.Invalidate();
            }
        }

        #endregion Properties

        #region Constructor

        /// <summary>
        /// Constructor
        /// Initialize data and register events
        /// Note: Could call this.InitPianoKeys() several times, consider constructing manually (see below)
        /// </summary>
        public VisualPiano()
        {
            InitializeComponent();
            this.InitPianoKeys();
        }

        /// <summary>
        /// Alternate constructor
        /// Used to set initial data explicitly before calling this.InitPianoKeys()
        /// </summary>
        /// <param name="octaves">Total number of octaves to display (min: 1, max: 7)</param>
        /// <param name="key_size">Size of each individual piano key</param>
        public VisualPiano(int octaves, Size key_size)
        {
            this.octave_count = octaves;
            this.key_size = key_size;
            InitializeComponent();
            this.InitPianoKeys();
        }

        #endregion Constructor

        #region Methods

        /// <summary>
        /// Return the size of the current drawing extents
        /// Used to ensure the control is big enough to display everything
        /// </summary>
        /// <returns>Returns the max size of current drawing extents</returns>
        private Size GetIdealSize()
        {
            return new Size(this.key_size.Width * (this.octave_count * PianoConstants.OCTAVES_MAX) + 1, this.key_size.Height + 1);
        }

        /// <summary>
        /// Initializes PianoKey data for the key_list array which stores all keys
        /// Note: This function should be called if there is a change to the piano size/key count at runtime
        /// To-do: Refactor code to occur at draw time and remove string parsing/handling junk
        /// </summary>
        private void InitPianoKeys()
        {
            // Remove any previous list elements
            this.key_list.Clear();

            int i, end_loop;

            // Manual fix for varying octave ranges
            switch (this.octave_count)
            {
                case PianoConstants.OCTAVE_FIRST:
                    // Range: 4th-5th octaves
                    i = 3 * 12;
                    end_loop = 4 * 12;
                    break;
                case PianoConstants.OCTAVE_SECOND:
                    // Range: 4th-6th octaves
                    i = 3 * 12;
                    end_loop = 5 * 12;
                    break;
                case PianoConstants.OCTAVE_THIRD:
                    // Range: 3rd-6th octaves
                    i = 2 * 12;
                    end_loop = 5 * 12;
                    break;
                case PianoConstants.OCTAVE_FOURTH:
                    // Range: 3rd-7th octaves
                    i = 2 * 12;
                    end_loop = 6 * 12;
                    break;
                case PianoConstants.OCTAVE_FIFTH:
                    // Range 2nd-7th octaves
                    i = 1 * 12;
                    end_loop = 6 * 12;
                    break;
                case PianoConstants.OCTAVE_SIXTH:
                    // Range: 2nd-last octaves
                    i = 1 * 12;
                    end_loop = 7 * 12;
                    break;
                // PianoConstants.OCTAVE_SEVENTH
                default:
                    // Range: first-last octaves
                    i = 0;
                    end_loop = 7 * 12;
                    break;
            }

            // Used to track the current key of iteration in order to filter between black/white keys
            int nthkey = 0;
            // Accumulate x position of bounds per white key (black keys use positions relative to white keys)
            int cur_x = 0;
            // Calculate black/semitone key dimensions
            int semitone_width = (int)(this.key_size.Width * 0.608);
            int semitone_height = (int)(this.key_size.Height * 0.7);
            int semitone_xoffset = this.key_size.Width + (int)(semitone_width / 2);

            for (; i < end_loop; i++)
            {
                PianoKey key;
                key.index = i;
                key.state = PianoKeyStates.DEFAULT;
                key.frequency = PianoConstants.FREQUENCIES[i];
                key.name = PianoConstants.STRINGS[i];
                key.note = (PianoKeyNotes)i;

                // Manual fix for black/white key determination
                switch (nthkey)
                {
                    case 2:
                        // Note: C#
                        key.is_semitone = true;
                        key.bounds = new Rectangle(cur_x - semitone_xoffset, 0, semitone_width, semitone_height);
                        break;
                    case 4:
                        // Note: D#
                        key.is_semitone = true;
                        key.bounds = new Rectangle(cur_x - semitone_xoffset, 0, semitone_width, semitone_height);
                        break;
                    case 7:
                        // Note: F#
                        key.is_semitone = true;
                        key.bounds = new Rectangle(cur_x - semitone_xoffset, 0, semitone_width, semitone_height);
                        break;
                    case 9:
                        // Note: G#
                        key.is_semitone = true;
                        key.bounds = new Rectangle(cur_x - semitone_xoffset, 0, semitone_width, semitone_height);
                        break;
                    case 11:
                        // Note: A#
                        key.is_semitone = true;
                        key.bounds = new Rectangle(cur_x - semitone_xoffset, 0, semitone_width, semitone_height);
                        break;
                    default:
                        // None-sharp note (white key)
                        key.is_semitone = false;
                        key.bounds = new Rectangle(cur_x, 0, this.key_size.Width, this.key_size.Height);
                        cur_x += this.key_size.Width;
                        break;
                }

                nthkey++;
                if (nthkey >= 12) nthkey = 0;
                key_list.Add(key);
            }
        }

        #endregion

        #region Control-derived Methods

        /// <summary>
        /// Override design-time resizing functionality to respect the AutoSize property
        /// </summary>
        protected override void SetBoundsCore(int x, int y, int width, int height, BoundsSpecified specified)
        {
            if (!this.auto_size)
                this.size = new Size(width, height);
            base.SetBoundsCore(x, y, this.size.Width, this.size.Height, specified);
        }

        /// <summary>
        /// Main drawing code
        /// </summary>
        protected override void OnPaint(PaintEventArgs pe)
        {
            // Calculate the keys that need to be re-drawn
            //int start = (int)(Math.Floor((pe.ClipRectangle.Left / (float)this.key_size.Width)) * this.key_size.Width);
            //int end = (int)(Math.Ceiling((pe.ClipRectangle.Right / (float)this.key_size.Width)) * this.key_size.Width);
            SolidBrush b_full_a = new SolidBrush(this.key_color_full_a);
            SolidBrush b_full_b = new SolidBrush(this.key_color_full_b);
            SolidBrush b_semi_a = new SolidBrush(this.key_color_semi_a);
            SolidBrush b_semi_b = new SolidBrush(this.key_color_semi_b);
            Pen p_black = new Pen(Color.Black, 1);
            Graphics g = pe.Graphics;

            foreach (PianoKey key in this.key_list)
            {
                if (!key.is_semitone)
                {
                    g.FillRectangle(b_full_a, key.bounds.Left, key.bounds.Top, key.bounds.Width, (int)(key.bounds.Height * 0.95));
                    g.FillRectangle(b_full_b, key.bounds.Left, (int)(key.bounds.Bottom * 0.95), key.bounds.Width, key.bounds.Height - (int)(key.bounds.Height * 0.95));
                    g.DrawRectangle(p_black, key.bounds);
                }
                else
                {
                    g.FillRectangle(b_semi_a, key.bounds.Left + (int)(key.bounds.Width * 0.24), key.bounds.Top + 1, key.bounds.Width - (int)(key.bounds.Width * 0.24), (int)(key.bounds.Height * 0.96));
                    g.FillRectangle(b_semi_b, key.bounds.Left, key.bounds.Top + 1, (int)(key.bounds.Width * 0.24), (int)(key.bounds.Height * 0.96));
                    g.FillRectangle(b_semi_b, key.bounds.Left, (int)(key.bounds.Height * 0.96), key.bounds.Width, key.bounds.Height - (int)(key.bounds.Height * 0.96));
                }
            }
        }

        #endregion
    }

    #endregion
}
